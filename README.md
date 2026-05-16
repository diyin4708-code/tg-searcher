# TG 搜索助手 v2 — Telegram 智能搜索机器人

个人账户自动搜索聊天记录，按关键词回复。

## 特性

| 特性 | 说明 |
|------|------|
| 🔍 多对话并发搜索 | asyncio.gather 同时搜多个对话 |
| ⏳ FloodWait 保护 | 自动检测限速，等冷却后重试 |
| 💾 结果缓存 | LRU + 60s TTL，重复搜索秒回 |
| 🚦 对话限速 | 每对话至少间隔 2 秒 |
| 📊 格式化回复 | Markdown 格式，日期+内容 |

## 安装

```bash
pip install telethon
```

## 配置

1. 去 https://my.telegram.org/apps 获取 API ID / Hash
2. 设置环境变量：

```bash
export TG_API_ID="12345678"
export TG_API_HASH="abcdef..."
```

## 运行

```bash
python3 main.py
```

首次运行输入手机号 + 验证码。之后自动保存 session。

## 使用

在任意对话发送：
```
搜索 BTC 行情     → 搜所有对话
查找 合约地址     → 同上
帮我找 空投规则   → 同上
```

## 结构

```
main.py    — 主程序（搜索 + 回复）
```

## 风险

⚠️ 用户账户的第三方客户端有封号风险。建议小号使用。
