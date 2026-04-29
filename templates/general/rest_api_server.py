"""
MCP Gateway Template — REST API Caller
Call any external HTTP API with full control.

Setup:
  pip install fastapi uvicorn httpx
  python templates/general/rest_api_server.py
"""
import uvicorn
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="REST API Caller MCP Server")


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "rest-api-caller"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        tools = {"get": do_get, "post": do_post, "put": do_put, "patch": do_patch, "delete": do_delete}
        if req.tool not in tools:
            return {"error": f"Unknown tool: {req.tool}"}
        return await tools[req.tool](**req.arguments)
    except Exception as e:
        return {"error": str(e)}


async def do_get(url: str, headers: dict = {}, params: dict = {}):
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(url, headers=headers, params=params)
        return {"result": {"status": r.status_code, "body": r.json() if "json" in r.headers.get("content-type", "") else r.text[:2000]}}


async def do_post(url: str, body: dict = {}, headers: dict = {}):
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, json=body, headers=headers)
        return {"result": {"status": r.status_code, "body": r.json() if "json" in r.headers.get("content-type", "") else r.text[:2000]}}


async def do_put(url: str, body: dict = {}, headers: dict = {}):
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.put(url, json=body, headers=headers)
        return {"result": {"status": r.status_code, "body": r.text[:2000]}}


async def do_patch(url: str, body: dict = {}, headers: dict = {}):
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.patch(url, json=body, headers=headers)
        return {"result": {"status": r.status_code, "body": r.text[:2000]}}


async def do_delete(url: str, headers: dict = {}):
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.delete(url, headers=headers)
        return {"result": {"status": r.status_code}}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8303)
