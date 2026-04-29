import json
import os
from pathlib import Path
from fastapi import HTTPException, status

POLICY_PATH = Path(__file__).parent / "policy.json"


def _load_policy() -> dict:
    if not POLICY_PATH.exists():
        return {}
    with open(POLICY_PATH) as f:
        return json.load(f)


def check_policy(api_key: str, server: str, tool: str):
    policy = _load_policy()
    if not policy:
        return

    key_policy = policy.get(api_key)
    if key_policy is None:
        return

    allowed_servers = key_policy.get("allow_servers", [])
    if allowed_servers and server not in allowed_servers:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Key not allowed to access server '{server}'.",
        )

    denied_tools = key_policy.get("deny_tools", [])
    if tool in denied_tools:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Key not allowed to use tool '{tool}'.",
        )
