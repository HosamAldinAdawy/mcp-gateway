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
    @router.get("/auto-key")
    async def auto_key():
    import os
    keys = os.getenv("MCP_API_KEYS", "")
    first_key = keys.split(",")[0].strip()
    return {"key": first_key}
