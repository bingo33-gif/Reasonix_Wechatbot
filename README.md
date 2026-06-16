# 🤖 Reasonix_Wechatbot

🚀 轻量、零依赖的微信 AI 自动回复机器人 | 基于 weixin-mcp + DeepSeek API

---

一个为 [Reasonix](https://reasonix.ai) 用户量身定制的微信自动回复机器人，也支持独立运行。  
3 秒轮询、消息去重、AI 驱动回复 —— 让你的微信账号拥有 GPT 级别的对话能力。

---

## ✨ Features

| 功能 | 状态 |
|------|:---:|
| AI 自动回复（DeepSeek） | ✅ |
| 消息去重（不怕重复回复） | ✅ |
| 自定义人设 / System Prompt | ✅ |
| 3 秒轮询（可调） | ✅ |
| 支持微信个人消息 | ✅ |
| 支持群聊消息 | ❌ |
| 图片 / 文件回复 | ❌ |
| Docker 部署 | ❌ |

## ⚠️ 特别说明

- 本项目基于 **weixin-mcp** 的 CLI 模式，与 [danni-cool/wechatbot-webhook](https://github.com/danni-cool/wechatbot-webhook) 的 webhook 方案不同
- 建议使用**微信小号**运行，避免主号被封
- DeepSeek API 按量计费，费用参考 [DeepSeek 定价](https://platform.deepseek.com/pricing)

---

## 🚀 一分钟 Demo

### 0. 前置依赖

```bash
# 确保已安装
node --version   # >= 18
python --version # >= 3.8
```

### 1. 安装 weixin-mcp

```bash
npm install -g weixin-mcp
```

### 2. 扫码登录微信

```bash
npx weixin-mcp login
npx weixin-mcp start
```

### 3. 设置 API Key & 启动机器人

```cmd
set DEEPSEEK_API_KEY=你的密钥
python wechat-autoreply.py
```

看到 `👂 开始监听微信消息...` 就成功了！  
打开微信，给你的机器人发消息试试。

---

## 🔧 配置

编辑 `wechat-autoreply.py` 顶部：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_MODEL` | AI 模型 | `deepseek-v4-flash` |
| `POLL_INTERVAL` | 轮询间隔（秒） | `3` |
| `SYSTEM_PROMPT` | 机器人人设 | 友好中文助手 |

### 自定义人设示例

```python
SYSTEM_PROMPT = """你是一只猫娘，用「喵~」结尾，
语气傲娇但不失礼貌。回复简短，1-3 句。"""
```

---

## 🏗️ 架构

```
微信消息 → weixin-mcp poll → Python 脚本
                                ↓
                           DeepSeek API
                           （生成 AI 回复）
                                ↓
微信收到回复 ← weixin-mcp send ←┘
```

| 组件 | 说明 |
|------|------|
| weixin-mcp | 微信消息收发 CLI 工具 |
| DeepSeek API | 生成 AI 回复 |
| wechat-autoreply.py | 主控脚本：轮询 + 调 AI + 回复 |

---

## 🛠️ API

本项目本身不提供 API。它通过调用 weixin-mcp 的 CLI 接口工作：

| 命令 | 说明 |
|------|------|
| `npx weixin-mcp poll` | 轮询新消息 |
| `npx weixin-mcp send <userId> <text>` | 发送消息 |
| `npx weixin-mcp status` | 查看守护进程状态 |

---

## 📄 License

MIT © [bingo33-gif](https://github.com/bingo33-gif)

---

## ⏫ 更新日志

### v1.0 (2026-06-16)

- 首次发布
- 支持 DeepSeek API 自动回复
- 消息去重机制
- 可自定义 System Prompt
