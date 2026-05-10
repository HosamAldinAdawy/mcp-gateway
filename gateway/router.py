import os
import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from gateway.models import ToolCallRequest, ToolCallResponse, ServerInfo
from gateway.proxy import call_tool
from registry.registry import get_server, get_all_servers
from security.auth import require_api_key
from security.audit import log_call
from security.policy import check_policy
from security.rate_limiter import check_rate_limit

router = APIRouter()


# ── Path helpers ──────────────────────────────────────────────────────────────
def _base_dir() -> Path:
    """Return the writable base directory (next to EXE in frozen mode)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path.cwd()


def _logs_path() -> Path:
    return _base_dir() / "logs" / "audit.jsonl"


def _env_path() -> Path:
    return _base_dir() / ".env"


@router.post("/call", response_model=ToolCallResponse)
async def tool_call(
    req: ToolCallRequest,
    api_key: str = Depends(require_api_key),
):
    check_rate_limit(api_key)
    check_policy(api_key, req.server, req.tool)
    server = get_server(req.server)
    if not server:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server '{req.server}' not found or not trusted in registry.",
        )
    if req.tool not in server.tools:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool '{req.tool}' not registered for server '{req.server}'.",
        )
    response = await call_tool(server, req.tool, req.arguments)
    log_call(
        api_key=api_key,
        server=req.server,
        tool=req.tool,
        arguments=req.arguments,
        success=response.success,
        error=response.error,
    )
    return response


@router.get("/servers", response_model=list[ServerInfo])
async def list_servers(api_key: str = Depends(require_api_key)):
    return get_all_servers()


@router.get("/servers/{name}", response_model=ServerInfo)
async def get_server_info(name: str, api_key: str = Depends(require_api_key)):
    server = get_server(name)
    if not server:
        raise HTTPException(status_code=404, detail=f"Server '{name}' not found.")
    return server


@router.post("/servers", include_in_schema=True)
async def add_server_api(
    req: dict,
    api_key: str = Depends(require_api_key),
):
    """Add a new server to the registry via API."""
    from registry.registry import add_server
    try:
        server = add_server(
            name=req["name"],
            description=req.get("description", ""),
            url=req["url"],
            transport=req.get("transport", "http"),
            tools=req["tools"],
            added_by=f"api:{api_key[:6]}",
        )
        return server
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/servers/{name}")
async def remove_server_api(name: str, api_key: str = Depends(require_api_key)):
    from registry.registry import remove_server
    removed = remove_server(name)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Server '{name}' not found.")
    return {"removed": name}


@router.get("/logs")
async def get_logs(api_key: str = Depends(require_api_key), limit: int = 100):
    """Read the audit log. Path resolved correctly in EXE."""
    import json
    log_path = _logs_path()
    if not log_path.exists():
        return []
    try:
        lines = [l for l in log_path.read_text().strip().split("\n") if l]
    except Exception:
        return []
    entries = []
    for l in lines[-limit:]:
        try:
            entries.append(json.loads(l))
        except Exception:
            pass
    return entries


@router.get("/auto-key")
async def auto_key():
    keys = os.getenv("MCP_API_KEYS", "")
    first_key = keys.split(",")[0].strip()
    return {"key": first_key}


@router.get("/settings")
async def get_settings(api_key: str = Depends(require_api_key)):
    """Return current gateway settings from .env"""
    settings = {
        "port":         os.getenv("PORT", "8000"),
        "rate_limit":   os.getenv("RATE_LIMIT_PER_MINUTE", "60"),
        "cors_origins": os.getenv("ALLOWED_ORIGINS", "*"),
        "log_level":    os.getenv("LOG_LEVEL", "info"),
    }
    env_path = _env_path()
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip(); v = v.strip()
            if k == "PORT":                    settings["port"]         = v
            elif k == "RATE_LIMIT_PER_MINUTE": settings["rate_limit"]   = v
            elif k == "ALLOWED_ORIGINS":       settings["cors_origins"] = v
            elif k == "LOG_LEVEL":             settings["log_level"]    = v
    return settings


@router.post("/setup")
async def setup_server(req: dict, api_key: str = Depends(require_api_key)):
    """
    Save credentials to .env and start the server.
    req: { "server": "jira", "credentials": { "JIRA_URL": "...", ... } }
    """
    import time

    server_name = req.get("server")
    credentials = req.get("credentials", {})

    if not server_name:
        raise HTTPException(status_code=400, detail="server name is required")

    env_path = _env_path()
    existing_lines = env_path.read_text().splitlines() if env_path.exists() else []

    updated_keys = set()
    new_lines = []
    for line in existing_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k = stripped.split("=")[0].strip()
            if k in credentials:
                new_lines.append(f"{k}={credentials[k]}")
                updated_keys.add(k)
                continue
        new_lines.append(line)

    for k, v in credentials.items():
        if k not in updated_keys:
            new_lines.append(f"{k}={v}")

    env_path.write_text("\n".join(new_lines) + "\n")

    for k, v in credentials.items():
        os.environ[k] = v

    # ── Start the server (skip for _settings) ────────────────────────────────
    started = False
    if server_name != "_settings":
        try:
            from gateway.server_manager import start_server
            started = start_server(server_name)
        except Exception:
            started = False
        time.sleep(1)

    return {
        "server": server_name,
        "started": started,
        "credentials_saved": True,
        "message": f"{server_name} {'settings saved' if server_name=='_settings' else ('server started successfully' if started else 'failed to start — check credentials')}",
    }


@router.post("/start-process")
async def start_process(req: dict, api_key: str = Depends(require_api_key)):
    """
    Start a custom server. Uses shlex.split — no shell=True (security).
    req: { "name": "my-server", "command": "python my_server.py" }
    """
    import subprocess
    import shlex
    import time

    name    = req.get("name", "")
    command = req.get("command", "").strip()

    if not command:
        raise HTTPException(status_code=400, detail="command is required")

    try:
        args = shlex.split(command, posix=(os.name != "nt"))
        proc = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1.5)

        if proc.poll() is None:
            return {"name": name, "started": True, "pid": proc.pid,
                    "message": f"{name} started (pid {proc.pid})"}
        else:
            return {"name": name, "started": False,
                    "message": f"{name} process exited immediately — check your command"}
    except Exception as e:
        return {"name": name, "started": False, "message": str(e)}


@router.post("/restart")
async def restart_gateway(api_key: str = Depends(require_api_key)):
    """Restart the gateway. Works in both EXE and dev mode."""
    import threading

    def do_restart():
        import time
        time.sleep(1)
        try:
            if getattr(sys, "frozen", False):
                # In EXE — relaunch with no args (sys.argv has bundled paths)
                os.execv(sys.executable, [sys.executable])
            else:
                os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception:
            os._exit(0)

    threading.Thread(target=do_restart, daemon=True).start()
    return {"message": "Restarting gateway..."}


@router.get("/check-update")
async def check_update(api_key: str = Depends(require_api_key)):
    """Check GitHub for a newer version."""
    try:
        from gateway.analytics import check_for_update
        result = check_for_update()
        return result or {"up_to_date": True}
    except Exception as e:
        return {"up_to_date": True, "error": str(e)}


@router.post("/track")
async def track_event(req: dict, api_key: str = Depends(require_api_key)):
    """Track a UI event."""
    try:
        from gateway.analytics import _track
        _track(req.get("event", "ui_event"), req.get("props", {}))
    except Exception:
        pass
    return {"ok": True}


# ── API Key Management (writes to .env) ──────────────────────────────────────
@router.post("/keys")
async def add_api_key(req: dict, api_key: str = Depends(require_api_key)):
    """Add a new API key to MCP_API_KEYS in .env."""
    new_key = req.get("key", "").strip()
    if not new_key:
        raise HTTPException(status_code=400, detail="key is required")

    env_path = _env_path()
    existing_lines = env_path.read_text().splitlines() if env_path.exists() else []

    found = False
    new_lines = []
    for line in existing_lines:
        stripped = line.strip()
        if stripped.startswith("MCP_API_KEYS="):
            current = stripped.split("=", 1)[1].strip()
            keys = [k.strip() for k in current.split(",") if k.strip()]
            if new_key not in keys:
                keys.append(new_key)
            new_lines.append(f"MCP_API_KEYS={','.join(keys)}")
            os.environ["MCP_API_KEYS"] = ",".join(keys)
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"MCP_API_KEYS={new_key}")
        os.environ["MCP_API_KEYS"] = new_key

    env_path.write_text("\n".join(new_lines) + "\n")
    return {"added": True, "key_prefix": new_key[:6]}


@router.delete("/keys/{key_prefix}")
async def remove_api_key(key_prefix: str, api_key: str = Depends(require_api_key)):
    """Remove an API key by its first 6 characters."""
    env_path = _env_path()
    if not env_path.exists():
        raise HTTPException(status_code=404, detail=".env not found")

    new_lines = []
    removed = False
    for line in env_path.read_text().splitlines():
        if line.strip().startswith("MCP_API_KEYS="):
            current = line.split("=", 1)[1].strip()
            keys = [k.strip() for k in current.split(",") if k.strip()]
            new_keys = [k for k in keys if not k.startswith(key_prefix)]
            if len(new_keys) < len(keys):
                removed = True
            if not new_keys:
                raise HTTPException(status_code=400, detail="Cannot remove last key")
            new_lines.append(f"MCP_API_KEYS={','.join(new_keys)}")
            os.environ["MCP_API_KEYS"] = ",".join(new_keys)
        else:
            new_lines.append(line)

    env_path.write_text("\n".join(new_lines) + "\n")
    if not removed:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"removed": True}
