"""
MCP Gateway Template — Asana Server
Manage Asana tasks, projects, and workspaces.

Setup:
  pip install fastapi uvicorn httpx
  export ASANA_TOKEN=your-personal-access-token
  python templates/general/asana_server.py
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Asana MCP Server")

TOKEN    = os.getenv("ASANA_TOKEN", "")
BASE_URL = "https://app.asana.com/api/1.0"


def client():
    return httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"},
        timeout=15.0,
    )


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "asana"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        if req.tool == "create_task":
            return await create_task(**req.arguments)
        elif req.tool == "get_task":
            return await get_task(**req.arguments)
        elif req.tool == "update_task":
            return await update_task(**req.arguments)
        elif req.tool == "list_tasks":
            return await list_tasks(**req.arguments)
        elif req.tool == "list_projects":
            return await list_projects(**req.arguments)
        elif req.tool == "add_comment":
            return await add_comment(**req.arguments)
        elif req.tool == "complete_task":
            return await complete_task(**req.arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def create_task(name: str, project_id: str, notes: str = "",
                      due_on: str = None, assignee: str = None):
    payload: dict = {"data": {"name": name, "notes": notes, "projects": [project_id]}}
    if due_on:  payload["data"]["due_on"]  = due_on
    if assignee:payload["data"]["assignee"] = assignee
    async with client() as c:
        r = await c.post("/tasks", json=payload)
        r.raise_for_status()
        d = r.json()["data"]
        return {"id": d["gid"], "name": d["name"],
                "url": f"https://app.asana.com/0/{project_id}/{d['gid']}"}


async def get_task(task_id: str):
    async with client() as c:
        r = await c.get(f"/tasks/{task_id}")
        r.raise_for_status()
        return r.json()["data"]


async def update_task(task_id: str, name: str = None, notes: str = None,
                      due_on: str = None, assignee: str = None):
    payload: dict = {"data": {}}
    if name:    payload["data"]["name"]     = name
    if notes:   payload["data"]["notes"]    = notes
    if due_on:  payload["data"]["due_on"]   = due_on
    if assignee:payload["data"]["assignee"] = assignee
    async with client() as c:
        r = await c.put(f"/tasks/{task_id}", json=payload)
        r.raise_for_status()
        return {"success": True, "id": task_id}


async def complete_task(task_id: str):
    async with client() as c:
        r = await c.put(f"/tasks/{task_id}", json={"data": {"completed": True}})
        r.raise_for_status()
        return {"success": True, "id": task_id, "completed": True}


async def list_tasks(project_id: str, completed: bool = False):
    params = {"project": project_id, "completed": str(completed).lower(),
              "opt_fields": "gid,name,completed,due_on,assignee.name"}
    async with client() as c:
        r = await c.get("/tasks", params=params)
        r.raise_for_status()
        tasks = r.json()["data"]
        return {"tasks": [{"id": t["gid"], "name": t["name"],
                            "completed": t["completed"], "due_on": t.get("due_on")} for t in tasks]}


async def list_projects(workspace_id: str = "", limit: int = 50):
    params = {"limit": limit, "opt_fields": "gid,name,color"}
    if workspace_id:
        params["workspace"] = workspace_id
    async with client() as c:
        r = await c.get("/projects", params=params)
        r.raise_for_status()
        return {"projects": [{"id": p["gid"], "name": p["name"]} for p in r.json()["data"]]}


async def add_comment(task_id: str, text: str):
    async with client() as c:
        r = await c.post(f"/tasks/{task_id}/stories", json={"data": {"text": text}})
        r.raise_for_status()
        return {"success": True, "id": r.json()["data"]["gid"]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8308)
