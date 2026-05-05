"""
MCP Gateway — Analytics, Error Reporting & Auto-Update
Uses PostHog for analytics/errors + GitHub Releases API for updates.
All analytics are anonymous — no personal data collected.
"""
import os
import sys
import threading
import platform
import traceback
from pathlib import Path

POSTHOG_KEY  = "phc_n6HsyDWGjADVTU3Ads4kVqmQcBmiPkkVZct9brHPLtnA"
POSTHOG_HOST = "https://us.i.posthog.com"
GITHUB_REPO  = "HosamAldinAdawy/mcp-gateway"
VERSION      = "1.0.0"

_ph = None
_device_id = None
_opt_out = False


def _get_device_id() -> str:
    """Generate a stable anonymous device ID."""
    global _device_id
    if _device_id:
        return _device_id

    id_file = Path.home() / ".mcp_gateway_id"
    if id_file.exists():
        _device_id = id_file.read_text().strip()
    else:
        import secrets
        _device_id = secrets.token_hex(16)
        try:
            id_file.write_text(_device_id)
        except Exception:
            pass
    return _device_id


def _get_ph():
    """Lazy-init PostHog client."""
    global _ph
    if _ph or _opt_out:
        return _ph
    try:
        import posthog
        posthog.project_api_key = POSTHOG_KEY
        posthog.host = POSTHOG_HOST
        posthog.disabled = False
        _ph = posthog
    except ImportError:
        try:
            import subprocess
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "posthog", "--quiet"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            import posthog
            posthog.project_api_key = POSTHOG_KEY
            posthog.host = POSTHOG_HOST
            _ph = posthog
        except Exception:
            pass
    return _ph


def _track(event: str, props: dict = None):
    """Send an event in a background thread — never blocks."""
    if _opt_out:
        return

    def send():
        try:
            ph = _get_ph()
            if ph:
                ph.capture(
                    _get_device_id(),
                    event,
                    {
                        "version": VERSION,
                        "os": platform.system(),
                        "python": platform.python_version(),
                        **(props or {}),
                    }
                )
        except Exception:
            pass

    threading.Thread(target=send, daemon=True).start()


# ── Public API ────────────────────────────────────────────────────────────────

def opt_out():
    """Disable all analytics for this session."""
    global _opt_out
    _opt_out = True


def track_install():
    """Call once on first launch."""
    _track("gateway_installed")


def track_launch():
    """Call every time the gateway starts."""
    _track("gateway_launched")


def track_template_connect(template: str):
    """Call when a user connects a template in Quick Setup."""
    _track("template_connected", {"template": template})


def track_tool_call(server: str, tool: str, success: bool):
    """Call after every tool call (sampled — 1 in 10)."""
    import random
    if random.random() > 0.1:
        return
    _track("tool_called", {"server": server, "tool": tool, "success": success})


def track_error(error: Exception, context: str = ""):
    """Report an error to PostHog."""
    _track("error_occurred", {
        "context": context,
        "error_type": type(error).__name__,
        "error_msg": str(error)[:200],
        "traceback": traceback.format_exc()[-500:],
    })


# ── Auto-update ───────────────────────────────────────────────────────────────

def check_for_update() -> dict | None:
    """
    Check GitHub Releases for a newer version.
    Returns { version, url, notes } or None if up to date.
    """
    def _check():
        try:
            import httpx
            r = httpx.get(
                f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
                timeout=5,
                headers={"User-Agent": "mcp-gateway"},
            )
            if r.status_code != 200:
                return None
            data = r.json()
            latest = data.get("tag_name", "").lstrip("v")
            if latest and latest != VERSION:
                assets = data.get("assets", [])
                exe_url = next(
                    (a["browser_download_url"] for a in assets if a["name"].endswith(".exe")),
                    data.get("html_url", "")
                )
                return {
                    "version": latest,
                    "url": exe_url,
                    "notes": data.get("body", "")[:300],
                }
            return None
        except Exception:
            return None

    return _check()


def check_for_update_async(callback):
    """Check for update in background, call callback(result) when done."""
    def run():
        result = check_for_update()
        if result:
            try:
                callback(result)
            except Exception:
                pass
    threading.Thread(target=run, daemon=True).start()
