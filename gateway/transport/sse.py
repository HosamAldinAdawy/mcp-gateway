"""
SSE Transport Layer — بيخلي الـ gateway remote MCP server حقيقي.

الـ MCP protocol بيستخدم SSE (Server-Sent Events) للـ remote communication.
ده بيخلي Claude Desktop و Cursor يتكلموا مع الـ gateway مباشرة
من غير ما يحتاجوا proxy أو bridge.
"""
import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from gateway.models import ToolCallRequest
from gateway.proxy import call_tool
from registry.registry import get_all_servers, get_server
from security.auth import require_api_key
from security.audit import log_call
from security.policy import check_policy
from security.rate_limiter import check_rate_limit

mcp_router = APIRouter()


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
        arguments = params.get("arguments", {}).get("arguments", {})

        # Split server__tool
        if "__" not in tool_full_name:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32602, "message": f"Invalid tool name format: {tool_full_name}"}
            }

        server_name, tool_name = tool_full_name.split("__", 1)

        check_rate_limit(api_key)
        check_policy(api_key, server_name, tool_name)

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

    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }


@mcp_router.get("/mcp")
async def mcp_sse(request: Request, api_key: str = Depends(require_api_key)):
    """
    SSE endpoint — ده الـ remote MCP entry point.
    Claude Desktop و Cursor بيتصلوا هنا مباشرة.
    """
    session_id = str(uuid.uuid4())

    async def event_stream() -> AsyncGenerator[str, None]:
        # Send endpoint event first (MCP protocol requirement)
        yield {
            "event": "endpoint",
            "data": f"/mcp/messages?session_id={session_id}"
        }

        # Keep alive
        while not await request.is_disconnected():
            yield {"event": "ping", "data": ""}
            import asyncio
            await asyncio.sleep(15)

    return EventSourceResponse(event_stream())


@mcp_router.post("/mcp/messages")
async def mcp_messages(
    request: Request,
    api_key: str = Depends(require_api_key)
):
    """بيستقبل الـ JSON-RPC messages من الـ MCP client."""
    body = await request.json()
    response = await handle_mcp_message(body, api_key)
    return response
