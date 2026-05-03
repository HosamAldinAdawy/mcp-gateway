import os
from fastapi import APIRouter, Depends, HTTPException, status
from gateway.models import ToolCallRequest, ToolCallResponse, ServerInfo
from gateway.proxy import call_tool
from registry.registry import get_server, get_all_servers
from security.auth import require_api_key
from security.audit import log_call
from security.policy import check_policy
from security.rate_limiter import check_rate_limit

router = APIRouter()


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
    import json
    from pathlib import Path
    log_path = Path("logs/audit.jsonl")
    if not log_path.exists():
        return []
    lines = [l for l in log_path.read_text().strip().split("\n") if l]
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


@router.post("/setup")
async def setup_server(req: dict, api_key: str = Depends(require_api_key)):
    """
    Save credentials to .env and start the server.
    req: { "server": "jira", "credentials": { "JIRA_URL": "...", ... } }
    """
    import sys
    import time
    from pathlib import Path

    server_name = req.get("server")
    credentials = req.get("credentials", {})

    if not server_name:
        raise HTTPException(status_code=400, detail="server name is required")

    # ── Write credentials to .env ─────────────────────────────────────────────
    if getattr(sys, "frozen", False):
        env_path = Path(sys.executable).parent / ".env"
    else:
        env_path = Path(".env")

    # Read existing lines preserving comments
    if env_path.exists():
        existing_lines = env_path.read_text().splitlines()
    else:
        existing_lines = []

    # Update existing keys or collect which new ones to append
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

    # Append any new keys not already in file
    for k, v in credentials.items():
        if k not in updated_keys:
            new_lines.append(f"{k}={v}")

    env_path.write_text("\n".join(new_lines) + "\n")

    # ── Set in current process env ────────────────────────────────────────────
    for k, v in credentials.items():
        os.environ[k] = v

    # ── Start the server ──────────────────────────────────────────────────────
    try:
        from gateway.server_manager import start_server
        started = start_server(server_name)
    except Exception as e:
        started = False

    time.sleep(1)

    return {
        "server": server_name,
        "started": started,
        "credentials_saved": True,
        "message": f"{server_name} server {'started successfully' if started else 'failed to start — check credentials'}",
    }
