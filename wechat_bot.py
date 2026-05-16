#!/usr/bin/env python3
"""
微信 AI 自动回复 — itchat-uos 版
扫码登录 → 监控消息 → DeepSeek回复
"""
import itchat, requests, json, time

DEEPSEEK_KEY = "sk-096ac189c99840b8ad2d697be34e6131"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

def ai_reply(msg_text):
    """DeepSeek 生成回复"""
    body = {
        "model": "deepseek-v4-pro",
        "messages": [
            {"role": "system", "content": "你是微信自动回复助手。回复简洁、友好、中文，不超过80字。不要用markdown。"},
            {"role": "user", "content": msg_text}
        ],
        "max_tokens": 150
    }
    try:
        r = requests.post(DEEPSEEK_URL, json=body,
            headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"},
            timeout=15)
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "收到~ 稍后回你 😊"

@itchat.msg_register(itchat.content.TEXT)
def auto_reply(msg):
    """收到文本消息时自动回复"""
    sender = msg['User'].get('NickName', '未知')
    text = msg['Text']
    print(f"[{time.strftime('%H:%M:%S')}] {sender}: {text[:50]}")
    
    # 回复
    reply = ai_reply(text)
    msg['User'].send(reply)
    print(f"         → {reply[:50]}")

def main():
    print("📱 正在启动微信...")
    # 用 uos 协议登录（二维码在终端显示）
    itchat.auto_login(hotReload=True, enableCmdQR=2)
    print("✅ 已登录，监控消息中...\n")
    
    itchat.run()

if __name__ == "__main__":
    main()
