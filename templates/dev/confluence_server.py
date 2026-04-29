"""
MCP Gateway Template — Confluence Server
Read, create, and update Confluence pages and spaces.

Setup:
  pip install fastapi uvicorn httpx
  export CONFLUENCE_URL=https://yourcompany.atlassian.net
  export CONFLUENCE_EMAIL=you@company.com
  export CONFLUENCE_TOKEN=your-api-token
  python templates/dev/confluence_server.py
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Confluence MCP Server")

BASE_URL = os.getenv("CONFLUENCE_URL", "")
EMAIL    = os.getenv("CONFLUENCE_EMAIL", "")
TOKEN    = os.getenv("CONFLUENCE_TOKEN", "")


def client():
    return httpx.AsyncClient(
        base_url=f"{BASE_URL}/wiki/rest/api",
        auth=(EMAIL, TOKEN),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=15.0,
    )


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "confluence"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        if req.tool == "get_page":
            return await get_page(**req.arguments)
        elif req.tool == "search_pages":
            return await search_pages(**req.arguments)
        elif req.tool == "create_page":
            return await create_page(**req.arguments)
        elif req.tool == "update_page":
            return await update_page(**req.arguments)
        elif req.tool == "get_space":
            return await get_space(**req.arguments)
        elif req.tool == "list_spaces":
            return await list_spaces()
        elif req.tool == "get_page_children":
            return await get_page_children(**req.arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_page(page_id: str, expand: str = "body.storage,version"):
    async with client() as c:
        r = await c.get(f"/content/{page_id}", params={"expand": expand})
        r.raise_for_status()
        data = r.json()
        return {
            "id":      data["id"],
            "title":   data["title"],
            "space":   data.get("space", {}).get("key"),
            "version": data.get("version", {}).get("number"),
            "body":    data.get("body", {}).get("storage", {}).get("value", ""),
            "url":     f"{BASE_URL}/wiki{data.get('_links', {}).get('webui', '')}",
        }


async def search_pages(query: str, space_key: str = "", limit: int = 10):
    cql = f'type=page AND text~"{query}"'
    if space_key:
        cql += f' AND space="{space_key}"'
    async with client() as c:
        r = await c.get("/content/search", params={"cql": cql, "limit": limit,
                                                     "expand": "version"})
        r.raise_for_status()
        results = r.json().get("results", [])
        return {"pages": [{"id": p["id"], "title": p["title"],
                            "space": p.get("space", {}).get("key"),
                            "url": f"{BASE_URL}/wiki{p.get('_links', {}).get('webui', '')}"
                            } for p in results], "total": len(results)}


async def create_page(space_key: str, title: str, body: str, parent_id: str = None):
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {"storage": {"value": body, "representation": "storage"}},
    }
    if parent_id:
        payload["ancestors"] = [{"id": parent_id}]
    async with client() as c:
        r = await c.post("/content", json=payload)
        r.raise_for_status()
        data = r.json()
        return {"id": data["id"], "title": data["title"],
                "url": f"{BASE_URL}/wiki{data.get('_links', {}).get('webui', '')}"}


async def update_page(page_id: str, title: str, body: str, version: int):
    payload = {
        "type": "page", "title": title,
        "version": {"number": version + 1},
        "body": {"storage": {"value": body, "representation": "storage"}},
    }
    async with client() as c:
        r = await c.put(f"/content/{page_id}", json=payload)
        r.raise_for_status()
        return {"success": True, "id": page_id, "new_version": version + 1}


async def get_space(space_key: str):
    async with client() as c:
        r = await c.get(f"/space/{space_key}", params={"expand": "homepage"})
        r.raise_for_status()
        return r.json()


async def list_spaces(limit: int = 25):
    async with client() as c:
        r = await c.get("/space", params={"limit": limit, "type": "global"})
        r.raise_for_status()
        results = r.json().get("results", [])
        return {"spaces": [{"key": s["key"], "name": s["name"]} for s in results]}


async def get_page_children(page_id: str):
    async with client() as c:
        r = await c.get(f"/content/{page_id}/child/page", params={"limit": 50})
        r.raise_for_status()
        results = r.json().get("results", [])
        return {"children": [{"id": p["id"], "title": p["title"]} for p in results]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8205)
