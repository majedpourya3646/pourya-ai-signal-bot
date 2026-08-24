# get_chat_id.py

import requests

BOT_TOKEN = input("Bot Token را وارد کنید: ").strip()

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

response = requests.get(url, timeout=15)
data = response.json()

if not data.get("ok"):
    print("❌ خطا:")
    print(data)
    raise SystemExit

updates = data.get("result", [])

if not updates:
    print("❌ هیچ پیامی پیدا نشد.")
    print("ابتدا داخل تلگرام یک پیام به ربات بفرستید و دوباره اجرا کنید.")
    raise SystemExit

last_update = updates[-1]

message = last_update.get("message") or last_update.get("edited_message")

if not message:
    print("❌ پیام معمولی Telegram پیدا نشد.")
    print(last_update)
    raise SystemExit

chat = message.get("chat", {})

print("\n✅ Telegram Chat ID پیدا شد:")
print("--------------------------------")
print(f"Chat ID : {chat.get('id')}")
print(f"Type    : {chat.get('type')}")
print(f"Name    : {chat.get('first_name', '')} {chat.get('last_name', '')}")
print(f"Username: @{chat.get('username', '')}")
print("--------------------------------")
