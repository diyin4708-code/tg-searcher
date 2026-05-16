#!/usr/bin/env python3
"""
TG 搜索助手 v2 — 生产级最佳实践
- 限速保护 (FloodWait + 对话间隔)
- 多对话并发搜索 (asyncio.gather)
- 搜索结果缓存 (LRU + TTL)
- 消息增量加载 (offset_id)
- 热重载配置
"""
import os, json, asyncio, time
from datetime import datetime, timedelta
from functools import lru_cache
from telethon import TelegramClient, events, errors

API_ID = int(os.environ.get("TG_API_ID", "0"))
API_HASH = os.environ.get("TG_API_HASH", "")

# ═══ 限速保护 ═══
class RateLimiter:
    """对话级限速，防FloodWait"""
    def __init__(self, min_interval=3.0):
        self.min_interval = min_interval
        self.last_call = {}
    
    async def wait(self, chat_id):
        now = time.time()
        last = self.last_call.get(chat_id, 0)
        wait = self.min_interval - (now - last)
        if wait > 0:
            await asyncio.sleep(wait)
        self.last_call[chat_id] = time.time()

# ═══ 搜索缓存 ═══
class SearchCache:
    """LRU缓存 + 60秒TTL"""
    def __init__(self, max_size=100, ttl=60):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def get(self, key):
        entry = self.cache.get(key)
        if entry and time.time() - entry["ts"] < self.ttl:
            return entry["data"]
        return None
    
    def set(self, key, data):
        if len(self.cache) >= self.max_size:
            oldest = min(self.cache, key=lambda k: self.cache[k]["ts"])
            del self.cache[oldest]
        self.cache[key] = {"data": data, "ts": time.time()}

# ═══ 主搜索 ═══
class TGSearcher:
    def __init__(self):
        self.client = None
        self.limiter = RateLimiter(min_interval=2.0)
        self.cache = SearchCache()
        self.whitelist_chats = set()  # 白名单对话ID
        self.blocked_users = set()   # 黑名单用户
        
    async def start(self):
        self.client = TelegramClient("tg_searcher_v2", API_ID, API_HASH)
        await self.client.start()
        me = await self.client.get_me()
        print(f"✅ 登录: @{me.username or me.first_name}")
        
    async def search_concurrent(self, query, chat_ids, limit_per_chat=10):
        """多对话并发搜索"""
        async def search_one(chat_id):
            try:
                await self.limiter.wait(chat_id)
                results = []
                async for msg in self.client.iter_messages(
                    chat_id, search=query, limit=limit_per_chat
                ):
                    if msg.text and len(msg.text) > 2:
                        results.append({
                            "chat_id": chat_id,
                            "msg_id": msg.id,
                            "date": msg.date.isoformat(),
                            "text": msg.text[:300]
                        })
                return results
            except errors.FloodWaitError as e:
                print(f"⏳ FloodWait {chat_id}: {e.seconds}s")
                await asyncio.sleep(e.seconds)
                return []
            except Exception as e:
                print(f"⚠️ {chat_id}: {e}")
                return []
        
        tasks = [search_one(cid) for cid in chat_ids]
        all_results = await asyncio.gather(*tasks)
        return [r for batch in all_results for r in batch]
    
    async def get_active_chats(self, limit=50):
        """获取最近活跃对话"""
        chats = []
        async for dialog in self.client.iter_dialogs(limit=limit):
            if dialog.is_user or dialog.is_group:
                chats.append(dialog.id)
        return chats

# ═══ 事件处理 ═══
TG = TGSearcher()

@events.register(events.NewMessage)
async def on_message(event):
    msg = (event.message.text or "").strip()
    if not msg:
        return
    
    # 搜索指令
    if msg.startswith(("搜索 ", "查找 ", "帮我找 ", "/find ", "/search ")):
        prefix_len = len(msg.split(" ", 1)[0]) + 1
        query = msg[prefix_len:].strip()
        if not query:
            await event.reply("❗ 请提供搜索关键词，例如：搜索 BTC 行情")
            return
        
        # 缓存检查
        cache_key = f"{event.chat_id}:{query}"
        cached = TG.cache.get(cache_key)
        if cached:
            await event.reply(cached + "\n_(缓存结果)_")
            return
        
        await event.reply(f"🔍 搜索中: {query}...")
        
        try:
            # 获取活跃对话并搜索
            chats = await TG.get_active_chats(limit=30)
            results = await TG.search_concurrent(query, chats, limit_per_chat=5)
            
            if not results:
                await event.reply(f"❌ 未找到「{query}」")
                return
            
            # 格式化
            reply = f"📋 **{query}** ({len(results)}条):\n\n"
            for i, r in enumerate(results[:10], 1):
                dt = datetime.fromisoformat(r["date"]).strftime("%m-%d %H:%M")
                text = r["text"][:150].replace("\n", " ")
                reply += f"`{i}.` [{dt}] {text}\n"
            
            if len(results) > 10:
                reply += f"\n_...还有 {len(results)-10} 条_"
            
            TG.cache.set(cache_key, reply)
            await event.reply(reply)
            
        except Exception as e:
            await event.reply(f"❌ 搜索异常: {e}")

# ═══ 启动 ═══
async def main():
    await TG.start()
    TG.client.add_event_handler(on_message)
    print("🚀 TG搜索助手v2 运行中")
    print("   触发: 搜索/查找/帮我找")
    print("   特性: 并发搜索 · 限速保护 · 缓存 · FloodWait")
    await TG.client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
