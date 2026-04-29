"""
MCP Gateway Template — Notion Server
Read, create, and update Notion pages and databases.

Setup:
  pip install fastapi uvicorn httpx
  export NOTION_TOKEN=secret_your-integration-token
  python templates/general/notion_server.py
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Notion MCP Server")

TOKEN    = os.getenv("NOTION_TOKEN", "")
BASE_URL = "https://api.notion.com/v1"
VERSION  = "2022-06-28"


def client():
    return httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {TOKEN}", "Notion-Version": VERSION,
                 "Content-Type": "application/json"},
        timeout=15.0,
    )


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "notion"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        if req.tool == "get_page":
            return await get_page(**req.arguments)
        elif req.tool == "search":
            return await search(**req.arguments)
        elif req.tool == "create_page":
            return await create_page(**req.arguments)
        elif req.tool == "update_page":
            return await update_page(**req.arguments)
        elif req.tool == "query_database":
            return await query_database(**req.arguments)
        elif req.tool == "create_database_entry":
            return await create_database_entry(**req.arguments)
        elif req.tool == "get_block_children":
            return await get_block_children(**req.arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_page(page_id: str):
    async with client() as c:
        r = await c.get(f"/pages/{page_id}")
        r.raise_for_status()
        data = r.json()
        title = ""
        props = data.get("properties", {})
        for p in props.values():
            if p.get("type") == "title":
                title = "".join(t.get("plain_text", "") for t in p.get("title", []))
                break
        return {"id": data["id"], "title": title,
                "url": data.get("url"),
                "created_time": data.get("created_time"),
                "last_edited_time": data.get("last_edited_time")}


async def search(query: str, filter_type: str = "page", limit: int = 10):
    payload = {"query": query, "page_size": limit}
    if filter_type in ("page", "database"):
        payload["filter"] = {"value": filter_type, "property": "object"}
    async with client() as c:
        r = await c.post("/search", json=payload)
        r.raise_for_status()
        results = r.json().get("results", [])
        simplified = []
        for item in results:
            obj_type = item.get("object")
            title = ""
            if obj_type == "page":
                for p in item.get("properties", {}).values():
                    if p.get("type") == "title":
                        title = "".join(t.get("plain_text", "") for t in p.get("title", []))
                        break
            elif obj_type == "database":
                title = "".join(t.get("plain_text", "") for t in item.get("title", []))
            simplified.append({"id": item["id"], "object": obj_type,
                                "title": title, "url": item.get("url")})
        return {"results": simplified, "total": len(simplified)}


async def create_page(parent_id: str, title: str, content: str = "", is_database: bool = False):
    parent = {"database_id": parent_id} if is_database else {"page_id": parent_id}
    payload = {
        "parent": parent,
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
    }
    if content:
        payload["children"] = [{"object": "block", "type": "paragraph",
                                 "paragraph": {"rich_text": [{"text": {"content": content}}]}}]
    async with client() as c:
        r = await c.post("/pages", json=payload)
        r.raise_for_status()
        data = r.json()
        return {"id": data["id"], "url": data.get("url")}


async def update_page(page_id: str, title: str = None, archived: bool = False):
    payload = {}
    if title:
        payload["properties"] = {"title": {"title": [{"text": {"content": title}}]}}
    if archived:
        payload["archived"] = True
    async with client() as c:
        r = await c.patch(f"/pages/{page_id}", json=payload)
        r.raise_for_status()
        return {"success": True, "id": page_id}


async def query_database(database_id: str, filter: dict = None, limit: int = 20):
    payload = {"page_size": limit}
    if filter:
        payload["filter"] = filter
    async with client() as c:
        r = await c.post(f"/databases/{database_id}/query", json=payload)
        r.raise_for_status()
        results = r.json().get("results", [])
        return {"entries": results, "total": len(results)}


async def create_database_entry(database_id: str, properties: dict):
    payload = {"parent": {"database_id": database_id}, "properties": properties}
    async with client() as c:
        r = await c.post("/pages", json=payload)
        r.raise_for_status()
        data = r.json()
        return {"id": data["id"], "url": data.get("url")}


async def get_block_children(block_id: str):
    async with client() as c:
        r = await c.get(f"/blocks/{block_id}/children", params={"page_size": 100})
        r.raise_for_status()
        blocks = r.json().get("results", [])
        simplified = []
        for b in blocks:
            btype = b.get("type", "")
            text = ""
            if btype in b:
                rich = b[btype].get("rich_text", [])
                text = "".join(t.get("plain_text", "") for t in rich)
            simplified.append({"id": b["id"], "type": btype, "text": text})
        return {"blocks": simplified}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8307)
