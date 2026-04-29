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
    servers = get_all_servers()
    results = []
    for s in servers:
        if await check_server(s):
            results.append(s)
    return results


async def count_healthy() -> int:
    return len(await get_healthy_servers())
