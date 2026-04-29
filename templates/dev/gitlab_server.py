"""
MCP Gateway Template — GitLab Server
Manage GitLab issues, merge requests, pipelines, and repos.

Setup:
  pip install fastapi uvicorn httpx
  export GITLAB_URL=https://gitlab.com
  export GITLAB_TOKEN=your-personal-access-token
  python templates/dev/gitlab_server.py
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="GitLab MCP Server")

GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")
TOKEN      = os.getenv("GITLAB_TOKEN", "")


def client():
    return httpx.AsyncClient(
        base_url=f"{GITLAB_URL}/api/v4",
        headers={"PRIVATE-TOKEN": TOKEN, "Content-Type": "application/json"},
        timeout=15.0,
    )


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "gitlab"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        if req.tool == "create_issue":
            return await create_issue(**req.arguments)
        elif req.tool == "list_issues":
            return await list_issues(**req.arguments)
        elif req.tool == "get_issue":
            return await get_issue(**req.arguments)
        elif req.tool == "create_merge_request":
            return await create_merge_request(**req.arguments)
        elif req.tool == "list_merge_requests":
            return await list_merge_requests(**req.arguments)
        elif req.tool == "get_pipeline":
            return await get_pipeline(**req.arguments)
        elif req.tool == "list_pipelines":
            return await list_pipelines(**req.arguments)
        elif req.tool == "trigger_pipeline":
            return await trigger_pipeline(**req.arguments)
        elif req.tool == "get_commits":
            return await get_commits(**req.arguments)
        elif req.tool == "add_comment":
            return await add_comment(**req.arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def create_issue(project_id: str, title: str, description: str = "",
                       labels: str = "", assignee_id: int = None):
    payload = {"title": title, "description": description}
    if labels:      payload["labels"]      = labels
    if assignee_id: payload["assignee_id"] = assignee_id
    async with client() as c:
        r = await c.post(f"/projects/{project_id}/issues", json=payload)
        r.raise_for_status()
        d = r.json()
        return {"id": d["iid"], "title": d["title"], "url": d["web_url"], "state": d["state"]}


async def list_issues(project_id: str, state: str = "opened", labels: str = "",
                      search: str = "", limit: int = 20):
    params = {"state": state, "per_page": limit}
    if labels: params["labels"] = labels
    if search: params["search"] = search
    async with client() as c:
        r = await c.get(f"/projects/{project_id}/issues", params=params)
        r.raise_for_status()
        return {"issues": [{"id": i["iid"], "title": i["title"], "state": i["state"],
                             "labels": i["labels"], "url": i["web_url"]} for i in r.json()]}


async def get_issue(project_id: str, issue_iid: int):
    async with client() as c:
        r = await c.get(f"/projects/{project_id}/issues/{issue_iid}")
        r.raise_for_status()
        return r.json()


async def create_merge_request(project_id: str, title: str, source_branch: str,
                                target_branch: str = "main", description: str = ""):
    payload = {"title": title, "source_branch": source_branch,
               "target_branch": target_branch, "description": description}
    async with client() as c:
        r = await c.post(f"/projects/{project_id}/merge_requests", json=payload)
        r.raise_for_status()
        d = r.json()
        return {"id": d["iid"], "title": d["title"], "url": d["web_url"], "state": d["state"]}


async def list_merge_requests(project_id: str, state: str = "opened", limit: int = 20):
    async with client() as c:
        r = await c.get(f"/projects/{project_id}/merge_requests",
                        params={"state": state, "per_page": limit})
        r.raise_for_status()
        return {"merge_requests": [{"id": m["iid"], "title": m["title"],
                                     "state": m["state"], "url": m["web_url"]} for m in r.json()]}


async def get_pipeline(project_id: str, pipeline_id: int):
    async with client() as c:
        r = await c.get(f"/projects/{project_id}/pipelines/{pipeline_id}")
        r.raise_for_status()
        return r.json()


async def list_pipelines(project_id: str, ref: str = "", limit: int = 10):
    params = {"per_page": limit}
    if ref: params["ref"] = ref
    async with client() as c:
        r = await c.get(f"/projects/{project_id}/pipelines", params=params)
        r.raise_for_status()
        return {"pipelines": [{"id": p["id"], "status": p["status"],
                                "ref": p["ref"], "created_at": p["created_at"]} for p in r.json()]}


async def trigger_pipeline(project_id: str, ref: str = "main", variables: dict = None):
    payload = {"ref": ref}
    if variables:
        payload["variables"] = [{"key": k, "value": v} for k, v in variables.items()]
    async with client() as c:
        r = await c.post(f"/projects/{project_id}/pipeline", json=payload)
        r.raise_for_status()
        d = r.json()
        return {"id": d["id"], "status": d["status"], "ref": d["ref"],
                "url": f"{GITLAB_URL}/{project_id}/-/pipelines/{d['id']}"}


async def get_commits(project_id: str, ref: str = "main", limit: int = 10):
    async with client() as c:
        r = await c.get(f"/projects/{project_id}/repository/commits",
                        params={"ref_name": ref, "per_page": limit})
        r.raise_for_status()
        return {"commits": [{"id": c_["short_id"], "message": c_["title"],
                              "author": c_["author_name"], "date": c_["created_at"]}
                             for c_ in r.json()]}


async def add_comment(project_id: str, issue_iid: int, body: str):
    async with client() as c:
        r = await c.post(f"/projects/{project_id}/issues/{issue_iid}/notes",
                         json={"body": body})
        r.raise_for_status()
        return {"success": True, "id": r.json()["id"]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8207)
