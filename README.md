# Reasonix_Wechatbot

基于 weixin-mcp + DeepSeek API 的微信自动回复机器人，让你的微信账号拥有 AI 对话能力。

## 功能

- 持续监听微信消息，自动 AI 回复
- 调用 DeepSeek API 生成自然、友好的中文回复
- 消息去重，不会重复回复
- 3 秒轮询间隔，响应迅速

## 快速开始

### 前置条件

| 依赖 | 说明 |
|------|------|
| Node.js | 运行 weixin-mcp |
| Python 3.8+ | 运行机器人脚本 |
| weixin-mcp | npm install -g weixin-mcp |
| DeepSeek API Key | platform.deepseek.com 获取 |

### 1. 登录微信
npx weixin-mcp login

### 2. 启动守护进程
npx weixin-mcp start

### 3. 设置 API Key
set DEEPSEEK_API_KEY=你的密钥

### 4. 运行机器人
python wechat-autoreply.py

按 Ctrl+C 停止。

## 配置

编辑 wechat-autoreply.py 顶部：

- DEEPSEEK_MODEL: AI 模型，默认 deepseek-v4-flash
- POLL_INTERVAL: 轮询间隔，默认 3 秒
- SYSTEM_PROMPT: 机器人人设

## 注意事项

- 建议使用微信小号
- API Key 通过环境变量传入，切勿硬编码
- DeepSeek API 按量计费

## 许可

MIT License
