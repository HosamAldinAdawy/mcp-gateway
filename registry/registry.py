import json
import os
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from gateway.models import ServerInfo


# ── Paths ─────────────────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    # In EXE: bundle is read-only, base dir is next to the EXE
    BUNDLE_DIR = Path(sys._MEIPASS)
    BASE_DIR   = Path(sys.executable).parent
else:
    BUNDLE_DIR = Path(__file__).parent
    BASE_DIR   = Path(__file__).parent

REGISTRY_PATH = BASE_DIR / "registry.json"


# ── On first EXE run, copy the bundled registry.json to a writable location ──
def _ensure_registry():
    if REGISTRY_PATH.exists():
        return
    # Try common locations the bundle may have
    candidates = [
        BUNDLE_DIR / "registry" / "registry.json",
        BUNDLE_DIR / "registry.json",
    ]
    for src in candidates:
        if src.exists():
            REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, REGISTRY_PATH)
            return
    # Fallback — create empty registry
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps({"servers": []}, indent=2))


_ensure_registry()


def _load() -> dict:
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def _save(data: dict):
    with open(REGISTRY_PATH, "w") as f:
        json.dump(data, f, indent=2)


def _to_server_info(s: dict) -> ServerInfo:
    """Build ServerInfo while ignoring extra fields not in the model."""
    valid_fields = ServerInfo.model_fields.keys()
    return ServerInfo(**{k: v for k, v in s.items() if k in valid_fields})


def get_all_servers() -> list[ServerInfo]:
    data = _load()
    return [_to_server_info(s) for s in data["servers"]]


def get_server(name: str) -> Optional[ServerInfo]:
    for s in get_all_servers():
        if s.name == name and s.trusted:
            return s
    return None


def add_server(
    name: str,
    description: str,
    url: str,
    transport: str,
    tools: list[str],
    added_by: str = "cli",
) -> ServerInfo:
    data = _load()
    if any(s["name"] == name for s in data["servers"]):
        raise ValueError(f"Server '{name}' already exists in registry.")
    entry = {
        "name": name,
        "description": description,
        "url": url,
        "transport": transport,
        "tools": tools,
        "trusted": True,
        "added_by": added_by,
        "added_at": datetime.now(timezone.utc).isoformat(),
    }
    data["servers"].append(entry)
    _save(data)
    return _to_server_info(entry)


def remove_server(name: str) -> bool:
    data = _load()
    before = len(data["servers"])
    data["servers"] = [s for s in data["servers"] if s["name"] != name]
    if len(data["servers"]) == before:
        return False
    _save(data)
    return True


def list_server_names() -> list[str]:
    return [s.name for s in get_all_servers()]
