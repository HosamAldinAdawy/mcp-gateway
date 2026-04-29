"""
MCP Gateway Template — GitHub Server
Manage repos, PRs, issues, and branches.

Setup:
  pip install fastapi uvicorn httpx
  export GITHUB_TOKEN=your-personal-access-token
  python templates/dev/github_server.py
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="GitHub MCP Server")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
BASE_URL = "https://api.github.com"


def gh_client():
    return httpx.AsyncClient(
        base_url=BASE_URL,
        headers={"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"},
        timeout=15.0,
    )


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "github"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        tools = {
            "create_issue": create_issue,
            "list_prs": list_prs,
            "get_pr": get_pr,
            "merge_pr": merge_pr,
            "create_branch": create_branch,
            "get_commits": get_commits,
        }
        if req.tool not in tools:
            return {"error": f"Unknown tool: {req.tool}"}
        return await tools[req.tool](**req.arguments)
    except Exception as e:
        return {"error": str(e)}


async def create_issue(owner: str, repo: str, title: str, body: str = "", labels: list = []):
    async with gh_client() as client:
        r = await client.post(f"/repos/{owner}/{repo}/issues", json={"title": title, "body": body, "labels": labels})
        r.raise_for_status()
        data = r.json()
        return {"result": {"number": data["number"], "url": data["html_url"], "title": data["title"]}}


async def list_prs(owner: str, repo: str, state: str = "open"):
    async with gh_client() as client:
        r = await client.get(f"/repos/{owner}/{repo}/pulls", params={"state": state})
        r.raise_for_status()
        prs = r.json()
        return {"result": [{"number": p["number"], "title": p["title"], "state": p["state"], "url": p["html_url"]} for p in prs]}


async def get_pr(owner: str, repo: str, pr_number: int):
    async with gh_client() as client:
        r = await client.get(f"/repos/{owner}/{repo}/pulls/{pr_number}")
        r.raise_for_status()
        p = r.json()
        return {"result": {"number": p["number"], "title": p["title"], "state": p["state"], "mergeable": p["mergeable"], "url": p["html_url"]}}


async def merge_pr(owner: str, repo: str, pr_number: int, commit_title: str = ""):
    async with gh_client() as client:
        r = await client.put(f"/repos/{owner}/{repo}/pulls/{pr_number}/merge", json={"commit_title": commit_title or f"Merge PR #{pr_number}"})
        r.raise_for_status()
        return {"result": r.json().get("message", "Merged.")}


async def create_branch(owner: str, repo: str, branch: str, from_branch: str = "main"):
    async with gh_client() as client:
        ref_r = await client.get(f"/repos/{owner}/{repo}/git/ref/heads/{from_branch}")
        ref_r.raise_for_status()
        sha = ref_r.json()["object"]["sha"]
        r = await client.post(f"/repos/{owner}/{repo}/git/refs", json={"ref": f"refs/heads/{branch}", "sha": sha})
        r.raise_for_status()
        return {"result": f"Branch '{branch}' created from '{from_branch}'."}


async def get_commits(owner: str, repo: str, branch: str = "main", limit: int = 10):
    async with gh_client() as client:
        r = await client.get(f"/repos/{owner}/{repo}/commits", params={"sha": branch, "per_page": limit})
        r.raise_for_status()
        commits = r.json()
        return {"result": [{"sha": c["sha"][:7], "message": c["commit"]["message"].split("\n")[0], "author": c["commit"]["author"]["name"]} for c in commits]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8201)
