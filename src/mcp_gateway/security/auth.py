import os
from fastapi import Header, HTTPException, status


def _get_valid_keys() -> set[str]:
    raw = os.getenv("MCP_API_KEYS", "")
    return {k.strip() for k in raw.split(",") if k.strip()}


async def require_api_key(x_api_key: str = Header(...)) -> str:
    valid_keys = _get_valid_keys()
    if not valid_keys:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No API keys configured. Set MCP_API_KEYS in .env",
        )
    if x_api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
    return x_api_key
