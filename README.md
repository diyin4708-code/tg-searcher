# TG 搜索助手 — 自动搜索聊天记录并回复

## 功能
- 监听关键词自动触发搜索（"搜索 xxx"、"查找 xxx"）
- 在所有对话/群聊中搜索历史消息
- 自动回复搜索结果

## 安装

```bash
pip install telethon
```

## 配置

1. 去 https://my.telegram.org/apps 获取 API ID 和 API Hash
2. 设置环境变量：

```bash
export TG_API_ID="你的API_ID"
export TG_API_HASH="你的API_HASH"
```

## 运行

```bash
python3 main.py
```

首次运行需要输入手机号和验证码登录。

## 触发词

```
搜索 xxx      # 在所有对话中搜索 xxx
查找 xxx      # 同上
帮我找 xxx    # 同上
/info         # 显示当前对话信息
```

## 自定义

编辑 `main.py` 中的 `SEARCH_TRIGGERS` 添加更多触发词。

## 风险声明

⚠️ 使用个人账户的第三方客户端可能导致封号。建议用小号测试。
