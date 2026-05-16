#!/usr/bin/env python3
"""
Telegram 智能搜索助手
- 监听指定对话的关键词
- 自动搜索聊天记录
- AI 分析后回复
"""
import os, json, re, asyncio
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import Message

# ═══ 配置 ═══
API_ID = int(os.environ.get("TG_API_ID", "0"))
API_HASH = os.environ.get("TG_API_HASH", "")
SESSION_NAME = "tg_searcher"
SEARCH_TRIGGERS = ["搜索", "查找", "帮我找", "/search", "/find"]

# ═══ 核心搜索 ═══
class TGSearcher:
    def __init__(self):
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        
    async def start(self):
        await self.client.start()
        me = await self.client.get_me()
        print(f"✅ 已登录: @{me.username or me.first_name}")
        
    async def search_messages(self, chat, query, limit=20):
        """在指定对话中搜索消息"""
        results = []
        async for msg in self.client.iter_messages(chat, search=query, limit=limit):
            if msg.text:
                results.append({
                    "id": msg.id,
                    "date": msg.date.isoformat(),
                    "sender": getattr(msg.sender, 'first_name', 'Unknown'),
                    "text": msg.text[:500]
                })
        return results
    
    async def search_all_chats(self, query, limit=5):
        """在所有对话中搜索"""
        results = []
        async for dialog in self.client.iter_dialogs():
            if dialog.is_user or dialog.is_group:
                msgs = await self.search_messages(dialog.id, query, min(limit, 10))
                for m in msgs:
                    m["chat"] = dialog.name
                    results.append(m)
                if len(results) >= limit:
                    break
        return results[:limit]
    
    async def reply_with_search(self, event, query):
        """搜索并回复"""
        await event.reply(f"🔍 正在搜索: {query}...")
        results = await self.search_all_chats(query, limit=5)
        
        if not results:
            await event.reply(f"❌ 未找到关于「{query}」的消息")
            return
        
        reply = f"📋 关于「{query}」的搜索结果 ({len(results)}条):\n\n"
        for i, r in enumerate(results, 1):
            date = datetime.fromisoformat(r["date"]).strftime("%m-%d %H:%M")
            reply += f"{i}. [{date}] {r.get('chat','')}/{r['sender']}:\n"
            reply += f"   {r['text'][:200]}\n\n"
        
        await event.reply(reply)

# ═══ 事件处理 ═══
searcher = TGSearcher()

@events.register(events.NewMessage)
async def handler(event):
    msg = event.message.text or ""
    
    # 关键词触发搜索
    for trigger in SEARCH_TRIGGERS:
        if msg.startswith(trigger):
            query = msg[len(trigger):].strip()
            if query:
                await searcher.reply_with_search(event, query)
            return
    
    # 命令: /info 查用户信息
    if msg.startswith("/info"):
        chat = await event.get_chat()
        info = f"📊 对话信息:\nID: {chat.id}\n名称: {chat.title or chat.first_name}\n类型: {type(chat).__name__}"
        await event.reply(info)

async def main():
    await searcher.start()
    searcher.client.add_event_handler(handler)
    print("🚀 TG搜索助手运行中...")
    print(f"   触发词: {SEARCH_TRIGGERS}")
    await searcher.client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
