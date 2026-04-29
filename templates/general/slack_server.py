"""
MCP Gateway Template — Slack Server
Send messages and notifications to Slack.

Setup:
  pip install fastapi uvicorn httpx
  export SLACK_BOT_TOKEN=xoxb-your-token
  python templates/general/slack_server.py
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Slack MCP Server")
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")


def slack_client():
    return httpx.AsyncClient(
        base_url="https://slack.com/api",
        headers={"Authorization": f"Bearer {SLACK_TOKEN}", "Content-Type": "application/json"},
        timeout=15.0,
    )


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "slack"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        tools = {
            "send_message": send_message,
            "list_channels": list_channels,
            "get_messages": get_messages,
            "create_channel": create_channel,
        }
        if req.tool not in tools:
            return {"error": f"Unknown tool: {req.tool}"}
        return await tools[req.tool](**req.arguments)
    except Exception as e:
        return {"error": str(e)}


async def send_message(channel: str, text: str, thread_ts: str = None):
    payload = {"channel": channel, "text": text}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    async with slack_client() as client:
        r = await client.post("/chat.postMessage", json=payload)
        data = r.json()
        if not data.get("ok"):
            return {"error": data.get("error", "Unknown Slack error")}
        return {"result": {"ts": data["ts"], "channel": data["channel"]}}


async def list_channels(limit: int = 20):
    async with slack_client() as client:
        r = await client.get("/conversations.list", params={"limit": limit, "types": "public_channel,private_channel"})
        data = r.json()
        channels = data.get("channels", [])
        return {"result": [{"id": c["id"], "name": c["name"], "is_private": c.get("is_private", False)} for c in channels]}


async def get_messages(channel: str, limit: int = 10):
    async with slack_client() as client:
        r = await client.get("/conversations.history", params={"channel": channel, "limit": limit})
        data = r.json()
        messages = data.get("messages", [])
        return {"result": [{"text": m.get("text", ""), "ts": m.get("ts"), "user": m.get("user")} for m in messages]}


async def create_channel(name: str, is_private: bool = False):
    async with slack_client() as client:
        r = await client.post("/conversations.create", json={"name": name, "is_private": is_private})
        data = r.json()
        if not data.get("ok"):
            return {"error": data.get("error")}
        return {"result": {"id": data["channel"]["id"], "name": data["channel"]["name"]}}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("SLACK_PORT", "8305")))
