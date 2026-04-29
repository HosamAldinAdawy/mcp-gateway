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
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

os.chdir(BASE_DIR)
sys.path.insert(0, str(BASE_DIR))

# ── Copy .env if missing ──────────────────────────────────────────────────────
env_file    = BASE_DIR / ".env"
env_example = BASE_DIR / ".env.example"
if not env_file.exists() and env_example.exists():
    shutil.copy(env_example, env_file)

# ── Auto-generate API key if still placeholder ────────────────────────────────
env_content = env_file.read_text() if env_file.exists() else ""
if "change-me-before-use" in env_content:
    new_key     = secrets.token_hex(24)
    env_content = env_content.replace("change-me-before-use", new_key)
    env_file.write_text(env_content)

# ── Build tray icon (purple rounded square with "M") ─────────────────────────
def make_icon():
    try:
        from PIL import Image, ImageDraw
        img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 0, 63, 63], radius=14, fill="#6366f1")
        # draw "M" manually as lines (no font needed)
        draw.line([(16, 48), (16, 16)], fill="white", width=5)
        draw.line([(16, 16), (32, 32)], fill="white", width=5)
        draw.line([(32, 32), (48, 16)], fill="white", width=5)
        draw.line([(48, 16), (48, 48)], fill="white", width=5)
        return img
    except Exception:
        from PIL import Image
        return Image.new("RGB", (64, 64), "#6366f1")

# ── Start uvicorn in background thread ───────────────────────────────────────
def run_server():
    import uvicorn
    uvicorn.run(
        "gateway.main:app",
        host="0.0.0.0",
        port=8000,
        log_level="error",
    )

threading.Thread(target=run_server, daemon=True).start()

# ── Open browser once server is up ───────────────────────────────────────────
def open_browser():
    time.sleep(2)
    webbrowser.open("http://localhost:8000")

threading.Thread(target=open_browser, daemon=True).start()

# ── System tray ──────────────────────────────────────────────────────────────
try:
    import pystray

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
        icon=make_icon(),
        title="MCP Gateway — running on :8000",
        menu=menu,
    )
    icon.run()

except ImportError:
    # Fallback if pystray not available
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        pass
