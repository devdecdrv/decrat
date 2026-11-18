# Run this ONCE on your PC to generate Telegram session
# python session_gen.py

from telethon.sync import TelegramClient
import os

API_ID   = input("API_ID daalo: ").strip()
API_HASH = input("API_HASH daalo: ").strip()
PHONE    = input("Phone number (+91...): ").strip()

# session same folder mein banega
client = TelegramClient("tg_session", int(API_ID), API_HASH)
client.connect()

if not client.is_user_authorized():
    client.send_code_request(PHONE)
    code = input("OTP daalo jo Telegram pe aaya: ").strip()
    client.sign_in(PHONE, code)

print("\n✅ Session ban gayi!")
print(f"File: {os.path.abspath('tg_session.session')}")
print("\nAb yeh file agent_tg.py ke saath same folder mein rakho.")
client.disconnect()
