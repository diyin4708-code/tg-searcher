#!/usr/bin/env python3
"""微信AI自动回复 — wcf版（HTTP API）"""
import requests, time, json

WCF = "http://172.19.208.1:8888"
DEEPSEEK_KEY = "sk-096ac189c99840b8ad2d697be34e6131"
seen = set()

def ai_reply(text):
    try:
        r = requests.post("https://api.deepseek.com/v1/chat/completions", json={
            "model": "deepseek-v4-pro",
            "messages": [
                {"role": "system", "content": "你是微信自动回复助手。回复简洁友好，中文，不超过80字。"},
                {"role": "user", "content": text}
            ],
            "max_tokens": 150
        }, headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"}, timeout=15)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "收到~ 😊"

def send_msg(wxid, text):
    requests.post(f"{WCF}/send", json={"receiver": wxid, "msg": text})

def get_messages():
    r = requests.get(f"{WCF}/get_messages", timeout=5)
    return r.json() if r.ok else []

print("🚀 微信自动回复启动 (wcf)")

while True:
    try:
        msgs = get_messages()
        for msg in msgs if isinstance(msgs, list) else []:
            mid = msg.get("id") or msg.get("msgid")
            if mid in seen:
                continue
            seen.add(mid)
            
            mtype = msg.get("type", 0)
            text = msg.get("content", "") or msg.get("msg", "")
            sender = msg.get("sender", "")
            
            if mtype == 1 and text and sender:
                print(f"[{time.strftime('%H:%M')}] {sender}: {text[:50]}")
                reply = ai_reply(text)
                send_msg(sender, reply)
                print(f"  → {reply[:50]}")
                time.sleep(1)  # 防限速
    except Exception as e:
        print(f"⚠️ {e}")
    
    time.sleep(3)
