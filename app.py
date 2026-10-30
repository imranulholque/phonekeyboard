"""Phone Keyboard - use your phone's keyboard on your Windows PC.

Runs in the system tray, serves a small web page on your local network and
types whatever you enter on the phone into the focused window on the PC.
"""
import ctypes
import hmac
import json
import os
import queue
import random
import secrets
import socket
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import customtkinter as ctk
import pystray
import qrcode
from PIL import Image, ImageDraw

import keys
from phone_page import DENIED, PAGE

APP_NAME = "PhoneKeyboard"
PORT_MIN, PORT_MAX = 6000, 6999
CFG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
CFG_FILE = os.path.join(CFG_DIR, "config.json")

# ---------------------------------------------------------------- config ----

def load_cfg():
    try:
        with open(CFG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except Exception:
        cfg = {}
    if not isinstance(cfg.get("port"), int) or not PORT_MIN <= cfg["port"] <= PORT_MAX:
        cfg["port"] = random.randint(PORT_MIN, PORT_MAX)
    if not cfg.get("token"):
        cfg["token"] = secrets.token_urlsafe(12)
    return cfg


def save_cfg(cfg):
    try:
        os.makedirs(CFG_DIR, exist_ok=True)
        with open(CFG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f)
    except Exception:
        pass


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))          # no packet is sent; just picks the LAN adapter
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

# --------------------------------------------------------------- startup ----

def ensure_startup(cfg):
    """Add the app to Windows startup once. After that, Task Manager > Startup
    apps is in charge: if you disable it there, we never turn it back on."""
    if not getattr(sys, "frozen", False):
        return
    try:
        import winreg
        run_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        cmd = '"%s" --background' % sys.executable
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key, 0,
                            winreg.KEY_READ | winreg.KEY_SET_VALUE) as k:
            try:
                current, _ = winreg.QueryValueEx(k, APP_NAME)
            except FileNotFoundError:
                current = None
            if current is not None:
                if current != cmd:                     # exe was moved
                    winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, cmd)
            elif not cfg.get("startup_registered"):
                winreg.SetValueEx(k, APP_NAME, 0, winreg.REG_SZ, cmd)
        cfg["startup_registered"] = True
        save_cfg(cfg)
    except Exception:
        pass

# ---------------------------------------------------------------- server ----

class State:
    def __init__(self, token):
        self.token = token
        self.last_seen = 0.0
        self.events = queue.Queue()

    def ok(self, tok):
        return bool(tok) and hmac.compare_digest(str(tok), self.token)


class QuietServer(ThreadingHTTPServer):
    allow_reuse_address = False      # never share a port with another program
    daemon_threads = True


def make_handler(state):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):
            pass

        def _send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
            if isinstance(body, str):
                body = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            u = urlparse(self.path)
            if u.path == "/_show":
                if self.client_address[0] in ("127.0.0.1", "::1"):
                    state.events.put("show")
                    return self._send(200, "ok")
                return self._send(403)
            if u.path == "/":
                tok = parse_qs(u.query).get("t", [""])[0]
                if state.ok(tok):
                    return self._send(200, PAGE, "text/html; charset=utf-8")
                return self._send(403, DENIED, "text/html; charset=utf-8")
            self._send(404)

        def do_POST(self):
            if not state.ok(self.headers.get("X-Token")):
                return self._send(401)
            try:
                n = int(self.headers.get("Content-Length") or 0)
                if n > 20000:
                    return self._send(413)
                data = json.loads(self.rfile.read(n) or b"{}")
            except Exception:
                return self._send(400)
            state.last_seen = time.time()
            try:
                if self.path == "/api/input":
                    keys.type_text(str(data.get("text", "")), int(data.get("back", 0)))
                elif self.path == "/api/key":
                    mods = [m for m in data.get("mods", []) if isinstance(m, str)]
                    keys.press_key(str(data.get("key", "")), mods)
                elif self.path != "/api/ping":
                    return self._send(404)
            except Exception:
                return self._send(500)
            self._send(200, "ok")

    return Handler


class Server:
    def __init__(self, state):
        self.shared = state
        self.httpd = None

    def start(self, port):
        self.stop()
        try:
            self.httpd = QuietServer(("0.0.0.0", port), make_handler(self.shared))
        except OSError:
            self.httpd = None
            return False
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        return True

    def stop(self):
        if self.httpd:
            try:
                self.httpd.shutdown()
                self.httpd.server_close()
            except Exception:
                pass
            self.httpd = None

# -------------------------------------------------------------------- UI ----

BG, PANEL, ACCENT, OK, BAD, MUTED = "#11152b", "#181e3b", "#8b9bff", "#5eead4", "#ff7a8a", "#9aa3d6"


def make_tray_icon():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((2, 12, 62, 52), 9, fill=ACCENT)
    for r in range(2):
        for c in range(5):
            x, y = 9 + c * 10, 19 + r * 12
            d.rounded_rectangle((x, y, x + 7, y + 8), 2, fill="#11152b")
    d.rounded_rectangle((19, 43, 45, 48), 2, fill="#11152b")
    return img


class App(ctk.CTk):
    def __init__(self, cfg, background):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.cfg = cfg
        self.shared = State(cfg["token"])
        self.server = Server(self.shared)
        self.ip = get_ip()
        self.qr_img = None

        self.title("Phone Keyboard")
        try:
            sc = self._get_window_scaling()
        except Exception:
            sc = 1.0
        w = 420
        h = max(420, min(720, int(self.winfo_screenheight() / sc * 0.86)))
        x = max(0, int((self.winfo_screenwidth() / sc - w) / 2))
        y = max(0, int((self.winfo_screenheight() / sc - h) / 2 * 0.6))
        self.geometry("%dx%d+%d+%d" % (w, h, x, y))
        self.minsize(360, 420)
        self.resizable(True, True)
        self.configure(fg_color=BG)
        self.protocol("WM_DELETE_WINDOW", self.hide)

        self._build()
        if not self.server.start(cfg["port"]):
            self._pick_free_port()
        self.refresh_qr()

        self.tray = pystray.Icon(APP_NAME, make_tray_icon(), "Phone Keyboard", pystray.Menu(
            pystray.MenuItem("Open", lambda: self.shared.events.put("show"), default=True),
            pystray.MenuItem("Quit", lambda: self.shared.events.put("quit"))))
        self.tray.run_detached()

        if background:
            self.withdraw()
        self.after(400, self.poll)

    # ---- layout
    def _build(self):
        # bottom bar stays visible on any screen size
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", pady=(4, 14))
        inner = ctk.CTkFrame(bottom, fg_color="transparent")
        inner.pack()
        ctk.CTkButton(inner, text="Hide to tray", width=140, height=38, fg_color="#262e57",
                      hover_color="#313b6e", command=self.hide).pack(side="left", padx=6)
        ctk.CTkButton(inner, text="Quit", width=140, height=38, fg_color="#5a2433",
                      hover_color="#7a3045", command=self.quit_app).pack(side="left", padx=6)

        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=4)

        ctk.CTkLabel(body, text="Phone Keyboard", font=ctk.CTkFont("Segoe UI", 26, "bold"),
                     text_color="#eef0ff").pack(pady=(10, 2))
        ctk.CTkLabel(body, text="Scan with your phone camera. No app needed.",
                     font=ctk.CTkFont("Segoe UI", 13), text_color=MUTED).pack()

        pill = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=20)
        pill.pack(pady=12)
        self.dot = ctk.CTkLabel(pill, text="●", text_color=BAD, font=ctk.CTkFont(size=14))
        self.dot.pack(side="left", padx=(14, 4), pady=6)
        self.status = ctk.CTkLabel(pill, text="Waiting for phone", text_color="#eef0ff",
                                   font=ctk.CTkFont("Segoe UI", 13))
        self.status.pack(side="left", padx=(0, 14))

        card = ctk.CTkFrame(body, fg_color="white", corner_radius=18)
        card.pack(pady=4)
        self.qr_label = ctk.CTkLabel(card, text="")
        self.qr_label.pack(padx=12, pady=12)

        self.url_label = ctk.CTkLabel(body, text="", text_color=MUTED, wraplength=360,
                                      font=ctk.CTkFont("Consolas", 12))
        self.url_label.pack(pady=(10, 0))
        ctk.CTkButton(body, text="Copy link", width=110, height=30, fg_color=PANEL,
                      hover_color="#232b55", command=self.copy_link).pack(pady=8)

        row = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=14)
        row.pack(padx=16, pady=6)
        ctk.CTkLabel(row, text="Port", text_color=MUTED).pack(side="left", padx=(14, 8), pady=10)
        self.port_entry = ctk.CTkEntry(row, width=70, justify="center", fg_color="#0e1226",
                                       border_width=0)
        self.port_entry.insert(0, str(self.cfg["port"]))
        self.port_entry.pack(side="left")
        ctk.CTkButton(row, text="Apply", width=58, fg_color=ACCENT, text_color="#0e1226",
                      hover_color="#a3afff", command=self.apply_port).pack(side="left", padx=6)
        ctk.CTkButton(row, text="Random", width=64, fg_color="#262e57", hover_color="#313b6e",
                      command=self.random_port).pack(side="left", padx=(0, 12))
        self.msg = ctk.CTkLabel(body, text="Ports 6000 to 6999", text_color=MUTED,
                                font=ctk.CTkFont("Segoe UI", 12))
        self.msg.pack()

        ctk.CTkButton(body, text="Make a new QR code", fg_color="transparent", border_width=1,
                      border_color="#2b3466", hover_color=PANEL, text_color=MUTED,
                      command=self.new_token).pack(pady=(10, 4))
        ctk.CTkLabel(body, text="Runs at startup. Turn that on or off in\nTask Manager > Startup apps.",
                     text_color=MUTED, font=ctk.CTkFont("Segoe UI", 12)).pack(pady=(6, 10))

    # ---- actions
    def url(self):
        return "http://%s:%d/?t=%s" % (self.ip, self.cfg["port"], self.cfg["token"])

    def refresh_qr(self):
        url = self.url()
        qr = qrcode.QRCode(border=1, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#11152b", back_color="white").convert("RGB")
        img = img.resize((230, 230), Image.NEAREST)
        self.qr_img = ctk.CTkImage(light_image=img, dark_image=img, size=(230, 230))
        self.qr_label.configure(image=self.qr_img)
        self.url_label.configure(text="http://%s:%d" % (self.ip, self.cfg["port"]))

    def copy_link(self):
        self.clipboard_clear()
        self.clipboard_append(self.url())
        self.say("Link copied", OK)

    def say(self, text, color=MUTED):
        self.msg.configure(text=text, text_color=color)

    def _set_port(self, port):
        if self.server.start(port):
            self.cfg["port"] = port
            save_cfg(self.cfg)
            self.port_entry.delete(0, "end")
            self.port_entry.insert(0, str(port))
            self.refresh_qr()
            return True
        return False

    def _pick_free_port(self):
        for _ in range(60):
            if self._set_port(random.randint(PORT_MIN, PORT_MAX)):
                return True
        self.say("No free port found in 6000-6999", BAD)
        return False

    def apply_port(self):
        try:
            port = int(self.port_entry.get().strip())
        except ValueError:
            return self.say("Enter a number from 6000 to 6999", BAD)
        if not PORT_MIN <= port <= PORT_MAX:
            return self.say("Port must be between 6000 and 6999", BAD)
        if port == self.cfg["port"] and self.server.httpd:
            return self.say("Already using this port", MUTED)
        old = self.cfg["port"]
        if self._set_port(port):
            self.say("Now using port %d. Scan the new QR." % port, OK)
        else:
            self._set_port(old)
            self.say("Port %d is busy. Try another." % port, BAD)

    def random_port(self):
        if self._pick_free_port():
            self.say("Now using port %d. Scan the new QR." % self.cfg["port"], OK)

    def new_token(self):
        self.cfg["token"] = secrets.token_urlsafe(12)
        self.shared.token = self.cfg["token"]
        save_cfg(self.cfg)
        self.refresh_qr()
        self.say("Old QR codes no longer work", OK)

    def show(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def hide(self):
        self.withdraw()

    def quit_app(self):
        try:
            self.tray.stop()
        except Exception:
            pass
        self.server.stop()
        self.destroy()

    # ---- background loop
    def poll(self):
        try:
            while True:
                ev = self.shared.events.get_nowait()
                if ev == "show":
                    self.show()
                elif ev == "quit":
                    return self.quit_app()
        except queue.Empty:
            pass
        ip = get_ip()
        if ip != self.ip:
            self.ip = ip
            self.refresh_qr()
        if time.time() - self.shared.last_seen < 8:
            self.dot.configure(text_color=OK)
            self.status.configure(text="Phone connected")
        else:
            self.dot.configure(text_color=BAD)
            self.status.configure(text="Waiting for phone")
        self.after(500, self.poll)

# ------------------------------------------------------------------ main ----

_mutex = None


def already_running():
    global _mutex
    k32 = ctypes.windll.kernel32
    _mutex = k32.CreateMutexW(None, False, "Local\\PhoneKeyboardSingleInstance")
    return k32.GetLastError() == 183          # ERROR_ALREADY_EXISTS


def main():
    cfg = load_cfg()
    if already_running():                      # just bring the first copy to the front
        try:
            urllib.request.urlopen("http://127.0.0.1:%d/_show" % cfg["port"], timeout=2)
        except Exception:
            pass
        return
    ensure_startup(cfg)
    save_cfg(cfg)
    App(cfg, "--background" in sys.argv).mainloop()


if __name__ == "__main__":
    main()
