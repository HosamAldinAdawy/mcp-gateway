"""
MCP Gateway — Desktop Launcher
Double-click to start. No terminal. Opens browser automatically.
Sits in system tray — right-click to open or quit.
"""
import os
import sys
import time
import secrets
import shutil
import threading
import webbrowser
from pathlib import Path

# ── Fix paths when running as PyInstaller bundle ─────────────────────────────
if getattr(sys, "frozen", False):
    BUNDLE_DIR = Path(sys._MEIPASS)
    BASE_DIR   = Path(sys.executable).parent
else:
    BUNDLE_DIR = Path(__file__).parent
    BASE_DIR   = Path(__file__).parent

os.chdir(BUNDLE_DIR)
sys.path.insert(0, str(BUNDLE_DIR))

# ── Always create .env if missing ────────────────────────────────────────────
env_file = BASE_DIR / ".env"

if not env_file.exists():
    env_example = BUNDLE_DIR / ".env.example"
    if env_example.exists():
        shutil.copy(env_example, env_file)
    else:
        new_key = secrets.token_hex(24)
        env_file.write_text(
            f"# MCP Gateway — auto-generated\n"
            f"MCP_API_KEYS={new_key}\n"
            f"HOST=0.0.0.0\n"
            f"PORT=8000\n"
        )

# ── Auto-generate API key if still placeholder ────────────────────────────────
env_content = env_file.read_text()
if "change-me-before-use" in env_content:
    new_key     = secrets.token_hex(24)
    env_content = env_content.replace("change-me-before-use", new_key)
    env_file.write_text(env_content)

# ── Build tray icon ───────────────────────────────────────────────────────────
def make_icon():
    try:
        from PIL import Image, ImageDraw
        img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 0, 63, 63], radius=14, fill="#6366f1")
        draw.line([(16, 48), (16, 16)], fill="white", width=5)
        draw.line([(16, 16), (32, 32)], fill="white", width=5)
        draw.line([(32, 32), (48, 16)], fill="white", width=5)
        draw.line([(48, 16), (48, 48)], fill="white", width=5)
        return img
    except Exception:
        try:
            from PIL import Image
            return Image.new("RGB", (64, 64), "#6366f1")
        except Exception:
            return None

# ── Start uvicorn in MAIN thread (no daemon) ─────────────────────────────────
def run_server():
    try:
        import uvicorn
        uvicorn.run(
            "gateway.main:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
        )
    except Exception as e:
        print(f"[ERROR] Server failed: {e}", flush=True)
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

# ── Open browser once server is up ───────────────────────────────────────────
def open_browser():
    time.sleep(3)
    webbrowser.open("http://localhost:8000")

threading.Thread(target=open_browser, daemon=True).start()

# ── System tray in background ────────────────────────────────────────────────
def run_tray():
    try:
        import pystray
        icon_img = make_icon()

        def on_open(icon, item):
            webbrowser.open("http://localhost:8000")

        def on_quit(icon, item):
            icon.stop()
            os._exit(0)

        menu = pystray.Menu(
            pystray.MenuItem("Open MCP Gateway", on_open, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", on_quit),
        )

        icon = pystray.Icon(
            name="MCP Gateway",
            icon=icon_img if icon_img else make_icon(),
            title="MCP Gateway — running on :8000",
            menu=menu,
        )
        icon.run()
    except Exception as e:
        print(f"[WARN] Tray failed: {e}", flush=True)

threading.Thread(target=run_tray, daemon=True).start()

# ── Run server in main thread ─────────────────────────────────────────────────
run_server()
