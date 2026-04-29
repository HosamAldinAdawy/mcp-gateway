import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from gateway.models import ServerInfo

REGISTRY_PATH = Path(__file__).parent / "registry.json"


def _load() -> dict:
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def _save(data: dict):
    with open(REGISTRY_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_all_servers() -> list[ServerInfo]:
    data = _load()
    return [ServerInfo(**s) for s in data["servers"]]


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
    return ServerInfo(**entry)


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
