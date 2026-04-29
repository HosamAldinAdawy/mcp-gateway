"""
MCP Gateway Template — Figma Server
Read Figma files, components, and comments.

Setup:
  pip install fastapi uvicorn httpx
  export FIGMA_TOKEN=your-personal-access-token
  python templates/general/figma_server.py
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Figma MCP Server")

TOKEN    = os.getenv("FIGMA_TOKEN", "")
BASE_URL = "https://api.figma.com/v1"


def client():
    return httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"X-Figma-Token": TOKEN},
        timeout=20.0,
    )


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "figma"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        if req.tool == "get_file":
            return await get_file(**req.arguments)
        elif req.tool == "get_file_nodes":
            return await get_file_nodes(**req.arguments)
        elif req.tool == "get_comments":
            return await get_comments(**req.arguments)
        elif req.tool == "add_comment":
            return await add_comment(**req.arguments)
        elif req.tool == "get_components":
            return await get_components(**req.arguments)
        elif req.tool == "list_projects":
            return await list_projects(**req.arguments)
        elif req.tool == "get_image_urls":
            return await get_image_urls(**req.arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_file(file_key: str, depth: int = 2):
    async with client() as c:
        r = await c.get(f"/files/{file_key}", params={"depth": depth})
        r.raise_for_status()
        data = r.json()
        doc  = data.get("document", {})
        return {
            "name":          data.get("name"),
            "last_modified": data.get("lastModified"),
            "version":       data.get("version"),
            "pages": [{"id": p["id"], "name": p["name"]}
                      for p in doc.get("children", [])],
        }


async def get_file_nodes(file_key: str, node_ids: list):
    async with client() as c:
        r = await c.get(f"/files/{file_key}/nodes",
                        params={"ids": ",".join(node_ids)})
        r.raise_for_status()
        return r.json().get("nodes", {})


async def get_comments(file_key: str):
    async with client() as c:
        r = await c.get(f"/files/{file_key}/comments")
        r.raise_for_status()
        comments = r.json().get("comments", [])
        return {"comments": [{"id": c_["id"], "message": c_["message"],
                               "user": c_["user"]["handle"],
                               "created_at": c_["created_at"]} for c_ in comments]}


async def add_comment(file_key: str, message: str, x: float = 0, y: float = 0):
    payload = {"message": message, "client_meta": {"x": x, "y": y}}
    async with client() as c:
        r = await c.post(f"/files/{file_key}/comments", json=payload)
        r.raise_for_status()
        return {"success": True, "id": r.json().get("id")}


async def get_components(file_key: str):
    async with client() as c:
        r = await c.get(f"/files/{file_key}/components")
        r.raise_for_status()
        components = r.json().get("meta", {}).get("components", [])
        return {"components": [{"key": c_["key"], "name": c_["name"],
                                 "description": c_.get("description", "")}
                                for c_ in components]}


async def list_projects(team_id: str):
    async with client() as c:
        r = await c.get(f"/teams/{team_id}/projects")
        r.raise_for_status()
        projects = r.json().get("projects", [])
        return {"projects": [{"id": p["id"], "name": p["name"]} for p in projects]}


async def get_image_urls(file_key: str, node_ids: list, scale: float = 1.0,
                          format: str = "png"):
    async with client() as c:
        r = await c.get(f"/images/{file_key}",
                        params={"ids": ",".join(node_ids), "scale": scale, "format": format})
        r.raise_for_status()
        return r.json().get("images", {})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8310)
