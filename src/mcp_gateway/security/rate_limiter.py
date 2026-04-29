import time
from collections import defaultdict
from fastapi import HTTPException, status

_requests: dict[str, list[float]] = defaultdict(list)
WINDOW_SECONDS = 60
MAX_REQUESTS = int(__import__("os").getenv("RATE_LIMIT_PER_MINUTE", "60"))


def check_rate_limit(api_key: str):
    now = time.time()
    window_start = now - WINDOW_SECONDS
    _requests[api_key] = [t for t in _requests[api_key] if t > window_start]

    if len(_requests[api_key]) >= MAX_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {MAX_REQUESTS} requests/minute.",
        )
    _requests[api_key].append(now)
