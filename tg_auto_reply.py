#!/usr/bin/env python3
"""
Telegram 个人号 AI 自动回复 — Telethon 版
用你的 TG 账号（不是 bot）自动回复消息
"""
import os, asyncio, requests, time
from telethon import TelegramClient, events

API_ID = int(os.environ.get("TG_API_ID", "0"))
API_HASH = os.environ.get("TG_API_HASH", "")
DEEPSEEK_KEY = "sk-096ac189c99840b8ad2d697be34e6131"

tg = TelegramClient("tg_auto_reply", API_ID, API_HASH)

def ai_reply(text):
    try:
        r = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            json={
                "model": "deepseek-v4-pro",
                "messages": [
                    {"role": "system", "content": "你是Telegram自动回复助手。回复简洁、友好、中文，不超过80字。"},
                    {"role": "user", "content": text}
                ],
                "max_tokens": 150
            },
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
            timeout=15
        )
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "收到~ 😊"

@events.register(events.NewMessage(incoming=True))
async def handler(event):
    # 不回复自己的消息
    if event.out:
        return
    
    msg = event.message.text or ""
    if not msg.strip():
        return
    
    sender = await event.get_sender()
    name = sender.first_name or sender.username or "未知"
    print(f"[{time.strftime('%H:%M')}] {name}: {msg[:50]}")
    
    reply = ai_reply(msg)
    await event.reply(reply)
    print(f"  → {reply[:50]}")

async def main():
    await tg.start()
    me = await tg.get_me()
    print(f"✅ 已登录: @{me.username or me.first_name}")
    print("🚀 监控私聊消息中...\n")
    await tg.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
