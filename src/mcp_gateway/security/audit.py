import json
import os
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(os.getenv("AUDIT_LOG_PATH", "logs/audit.jsonl"))


def _ensure_log_dir():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def log_call(
    api_key: str,
    server: str,
    tool: str,
    arguments: dict,
    success: bool,
    error: str | None = None,
):
    _ensure_log_dir()
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "key_hint": f"{api_key[:6]}***",
        "server": server,
        "tool": tool,
        "args_keys": list(arguments.keys()),
        "success": success,
        "error": error,
    }
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
