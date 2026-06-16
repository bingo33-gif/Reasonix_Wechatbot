#!/usr/bin/env python3
"""
🤖 R仔 微信自动回复机器人
基于 weixin-mcp + DeepSeek API，持续监听微信消息并 AI 自动回复
版本: 1.0 | 为 Reasonix 用户定制
"""

import subprocess
import json
import os
import re
import time
import sys
import signal
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

# Windows 下强制 UTF-8 输出（修复中文/emoji 显示）
if sys.platform == "win32":
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)
    sys.stderr = open(sys.stderr.fileno(), mode="w", encoding="utf-8", buffering=1)

# ==================== 配置 ====================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-flash"
POLL_INTERVAL = 3          # 轮询间隔（秒）
PROCESSED_FILE = os.path.expanduser("~/.weixin-mcp/autoreply_processed.json")

# 找到 npx 的完整路径（Windows 下 subprocess 不会自动搜 PATH）
NPX_PATH = "npx.cmd"  # Windows 上优先用 .cmd

# R仔的人设（发给 DeepSeek 的系统提示）
SYSTEM_PROMPT = """你是 R仔，一个友好、耐心的 AI 助手，通过微信与用户交流。

你的特点：
- 用中文回复，语气像朋友聊天一样自然
- 回复简洁但不敷衍，通常 2-5 句话
- 用户是编程新手，解释技术问题时用通俗的语言
- 当用户问"为什么"时，认真解释原因
- 回复结尾不加署名

你现在在微信上，所以回复要适合微信聊天场景。"""


# ==================== AI 回复生成 ====================
def generate_reply(user_message):
    """调用 DeepSeek API 生成 AI 回复"""
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 600,
        "temperature": 0.7
    }
    
    try:
        req = Request(
            f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
            }
        )
        resp = urlopen(req, timeout=30)
        data = json.loads(resp.read())
        return data["choices"][0]["message"]["content"].strip()
    except URLError as e:
        print(f"  ❌ 网络错误: {e}")
        return None
    except Exception as e:
        print(f"  ❌ API 错误: {e}")
        return None


# ==================== 微信消息操作 ====================
def poll_messages(reset=False):
    """
    轮询微信新消息
    返回: [(user_id, text), ...] 或 []
    """
    args = [NPX_PATH, "weixin-mcp", "poll"]
    if reset:
        args.append("--reset")
    
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, encoding="utf-8", 
            timeout=15, cwd=os.path.dirname(__file__) or None
        )
        output = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if stderr:
            print(f"  ⚠️ poll stderr: {stderr[:100]}")
        
        if "No new messages" in output or not output:
            return []
        
        # 解析格式: "← shortId: text"
        messages = []
        for line in output.split("\n"):
            match = re.match(r"←\s+(\S+):\s+(.+)", line)
            if match:
                user_id = match.group(1)
                text = match.group(2)
                messages.append((user_id, text))
        
        return messages
    
    except subprocess.TimeoutExpired:
        print("  ⚠️ poll 超时")
        return []
    except Exception as e:
        print(f"  ⚠️ poll 异常: {e}")
        return []


def send_reply(user_id, text):
    """通过 weixin-mcp CLI 发送微信回复"""
    try:
        result = subprocess.run(
            [NPX_PATH, "weixin-mcp", "send", user_id, text],
            capture_output=True, text=True, encoding="utf-8", timeout=15
        )
        if result.returncode != 0:
            print(f"  ⚠️ send 失败: {result.stderr[:100]}")
            return False
        return True
    except Exception as e:
        print(f"  ❌ send 异常: {e}")
        return False


# ==================== 去重机制 ====================
def load_processed():
    """加载已处理的消息 ID 集合"""
    try:
        if os.path.exists(PROCESSED_FILE):
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
    except Exception:
        pass
    return set()


def save_processed(msg_ids):
    """保存已处理的消息 ID（只保留最近 500 条）"""
    try:
        os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            json.dump(list(msg_ids)[-500:], f)
    except Exception as e:
        print(f"  ⚠️ 保存去重记录失败: {e}")


# ==================== 主循环 ====================
def main():
    print("=" * 50)
    print("  🤖 R仔 微信自动回复机器人 v1.0")
    print("=" * 50)
    
    # --- 自检 ---
    print("\n📋 启动自检:")
    
    if not DEEPSEEK_API_KEY:
        print("  ❌ 未设置 DEEPSEEK_API_KEY 环境变量！")
        print("     请在终端运行: set DEEPSEEK_API_KEY=你的密钥")
        sys.exit(1)
    print(f"  ✅ DeepSeek API Key: 已配置")
    
    # 检查守护进程
    status = subprocess.run(
        [NPX_PATH, "weixin-mcp", "status"],
        capture_output=True, text=True, encoding="utf-8", timeout=10
    )
    if "running" not in status.stdout:
        print("  ❌ weixin-mcp 守护进程未运行！")
        print("     请先运行: npx weixin-mcp start")
        sys.exit(1)
    print(f"  ✅ weixin-mcp 守护进程: 运行中")
    
    print(f"  ✅ 模型: {DEEPSEEK_MODEL}")
    print(f"  ✅ 轮询间隔: {POLL_INTERVAL}秒")
    
    # 加载去重记录
    processed = load_processed()
    print(f"  ✅ 去重记录: {len(processed)} 条历史消息")
    
    # 初始化游标
    print("\n🔄 初始化消息游标（跳过历史消息）...")
    poll_messages(reset=True)
    time.sleep(1)
    
    print("\n👂 开始监听微信消息... (按 Ctrl+C 停止)\n")
    
    # --- 主循环 ---
    while True:
        try:
            messages = poll_messages()
            
            for user_id, text in messages:
                # 去重
                fingerprint = f"{user_id}:{text[:30]}"
                if fingerprint in processed:
                    continue
                
                now = datetime.now().strftime("%H:%M:%S")
                user_short = user_id[:8]
                print(f"[{now}] 📩 {user_short}: {text}")
                
                # 调 AI 生成回复
                reply = generate_reply(text)
                
                if reply:
                    success = send_reply(user_id, reply)
                    status_icon = "✅" if success else "❌"
                    reply_preview = reply[:40].replace("\n", " ")
                    print(f"[{now}]    {status_icon} 回复: {reply_preview}...")
                    
                    processed.add(fingerprint)
                    save_processed(processed)
                else:
                    print(f"[{now}]    ⚠️ 跳过（AI 生成失败）")
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 R仔 已停止。再见！")
            break
        except Exception as e:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] ⚠️ 循环异常: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    # Windows 兼容信号处理
    try:
        signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    except Exception:
        pass
    main()
