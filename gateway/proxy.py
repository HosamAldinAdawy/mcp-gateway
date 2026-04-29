import httpx
from gateway.models import ServerInfo, ToolCallResponse


async def call_tool(
    server: ServerInfo,
    tool: str,
    arguments: dict,
) -> ToolCallResponse:
    payload = {"tool": tool, "arguments": arguments}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(f"{server.url}/call", json=payload)
            r.raise_for_status()
            data = r.json()
            return ToolCallResponse(
                success=True,
                result=data.get("result"),
                server=server.name,
                tool=tool,
            )
    except httpx.HTTPStatusError as e:
        return ToolCallResponse(
            success=False,
            result=None,
            server=server.name,
            tool=tool,
            error=f"Server returned {e.response.status_code}: {e.response.text}",
        )
    except Exception as e:
        return ToolCallResponse(
            success=False,
            result=None,
            server=server.name,
            tool=tool,
            error=str(e),
        )
