import asyncio
import httpx
from registry.registry import get_all_servers
from gateway.models import ServerInfo


async def check_server(server: ServerInfo) -> bool:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{server.url}/health")
            return r.status_code == 200
    except Exception:
        return False


async def get_healthy_servers() -> list[ServerInfo]:
    """Run all health checks in parallel — much faster on startup."""
    servers = get_all_servers()
    if not servers:
        return []
    results = await asyncio.gather(
        *(check_server(s) for s in servers),
        return_exceptions=True,
    )
    return [s for s, ok in zip(servers, results) if ok is True]


async def count_healthy() -> int:
    return len(await get_healthy_servers())
