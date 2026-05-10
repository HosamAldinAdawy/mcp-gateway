"""
SSE Transport Layer — بيخلي الـ gateway remote MCP server حقيقي.

الـ MCP protocol بيستخدم SSE (Server-Sent Events) للـ remote communication.
ده بيخلي Claude Desktop و Cursor يتكلموا مع الـ gateway مباشرة
من غير ما يحتاجوا proxy أو bridge.

Auth بيقبل الاتنين:
- X-API-Key header (الطريقة المعيارية)
- ?api_key= query param (لما الـ client مش بيدعم headers في SSE)
"""
import os
import json
import uuid
import asyncio
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Request, Header, Query, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from gateway.proxy import call_tool
from registry.registry import get_all_servers, get_server
from security.audit import log_call
from security.policy import check_policy
from security.rate_limiter import check_rate_limit

mcp_router = APIRouter()


# ── Flexible API key auth (header OR query param) ─────────────────────────────
def _get_api_key(
    x_api_key: Optional[str] = None,
    api_key: Optional[str] = None,
) -> str:
    key = x_api_key or api_key
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required (X-API-Key header or ?api_key= query)",
        )
    valid_keys = {k.strip() for k in os.getenv("MCP_API_KEYS", "").split(",") if k.strip()}
    if not valid_keys:
        raise HTTPException(status_code=500, detail="No API keys configured on gateway")
    if key not in valid_keys:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return key


def build_tools_list() -> list[dict]:
    """بيبني قايمة الـ tools من كل الـ servers المسجلة."""
    tools = []
    for server in get_all_servers():
        for tool_name in server.tools:
            tools.append({
                "name": f"{server.name}__{tool_name}",
                "description": f"[{server.name}] {tool_name}",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "arguments": {
                            "type": "object",
                            "description": f"Arguments for {tool_name}"
                        }
                    }
                }
            })
    return tools


async def handle_mcp_message(message: dict, api_key: str) -> dict:
    """بيمشي الـ MCP JSON-RPC protocol."""
    method = message.get("method", "")
    msg_id = message.get("id")
    params = message.get("params", {})

    # Initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "mcp-gateway",
                    "version": "1.0.0"
                }
            }
        }

    # List tools
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": build_tools_list()}
        }

    # Call tool
    elif method == "tools/call":
        tool_full_name = params.get("name", "")
        # Tolerate both shapes: { arguments: {...} } and { arguments: { arguments: {...} } }
        raw_args = params.get("arguments", {}) or {}
        arguments = raw_args.get("arguments", raw_args) if isinstance(raw_args, dict) else {}

        if "__" not in tool_full_name:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32602, "message": f"Invalid tool name format: {tool_full_name}"}
            }

        server_name, tool_name = tool_full_name.split("__", 1)

        try:
            check_rate_limit(api_key)
            check_policy(api_key, server_name, tool_name)
        except HTTPException as e:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32603, "message": e.detail}
            }

        server = get_server(server_name)
        if not server:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32602, "message": f"Server '{server_name}' not in registry"}
            }

        response = await call_tool(server, tool_name, arguments)
        log_call(api_key, server_name, tool_name, arguments, response.success, response.error)

        if response.success:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(response.result, ensure_ascii=False)}]
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32603, "message": response.error or "Tool call failed"}
            }

    # Ping
    elif method == "ping":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

    # Notifications (no response needed)
    elif method.startswith("notifications/"):
        return None

    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }


@mcp_router.get("/mcp")
async def mcp_sse(
    request: Request,
    x_api_key: Optional[str] = Header(default=None),
    api_key: Optional[str] = Query(default=None),
):
    """
    SSE endpoint — ده الـ remote MCP entry point.
    Claude Desktop و Cursor بيتصلوا هنا مباشرة.
    Auth: X-API-Key header OR ?api_key= query.
    """
    key = _get_api_key(x_api_key, api_key)
    session_id = str(uuid.uuid4())

    async def event_stream() -> AsyncGenerator[dict, None]:
        # Send endpoint event first (MCP protocol requirement)
        # Include the api_key so the POST callback can authenticate
        yield {
            "event": "endpoint",
            "data": f"/mcp/messages?session_id={session_id}&api_key={key}"
        }

        # Keep alive
        try:
            while not await request.is_disconnected():
                yield {"event": "ping", "data": ""}
                await asyncio.sleep(15)
        except asyncio.CancelledError:
            return

    return EventSourceResponse(event_stream())


@mcp_router.post("/mcp/messages")
async def mcp_messages(
    request: Request,
    x_api_key: Optional[str] = Header(default=None),
    api_key: Optional[str] = Query(default=None),
):
    """بيستقبل الـ JSON-RPC messages من الـ MCP client."""
    key = _get_api_key(x_api_key, api_key)
    body = await request.json()
    response = await handle_mcp_message(body, key)
    # Notifications return None — respond with 204 No Content
    if response is None:
        return {"ok": True}
    return response
