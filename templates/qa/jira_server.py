"""
MCP Gateway Template — Jira Server
Manage Jira issues: create bugs, search, update status, add comments.

Setup:
  pip install fastapi uvicorn httpx
  export JIRA_URL=https://yourcompany.atlassian.net
  export JIRA_EMAIL=you@company.com
  export JIRA_TOKEN=your-api-token
  python templates/qa/jira_server.py
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Jira MCP Server")

JIRA_URL = os.getenv("JIRA_URL", "")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "")
JIRA_TOKEN = os.getenv("JIRA_TOKEN", "")


def jira_client():
    return httpx.AsyncClient(
        base_url=JIRA_URL,
        auth=(JIRA_EMAIL, JIRA_TOKEN),
        headers={"Content-Type": "application/json"},
        timeout=15.0,
    )


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "jira"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        if req.tool == "create_issue":
            return await create_issue(**req.arguments)
        elif req.tool == "search_issues":
            return await search_issues(**req.arguments)
        elif req.tool == "get_issue":
            return await get_issue(**req.arguments)
        elif req.tool == "update_issue":
            return await update_issue(**req.arguments)
        elif req.tool == "add_comment":
            return await add_comment(**req.arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")
    except Exception as e:
        return {"error": str(e)}


async def create_issue(project: str, summary: str, description: str = "", issue_type: str = "Bug", priority: str = "Medium"):
    async with jira_client() as client:
        payload = {
            "fields": {
                "project": {"key": project},
                "summary": summary,
                "description": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]},
                "issuetype": {"name": issue_type},
                "priority": {"name": priority},
            }
        }
        r = await client.post("/rest/api/3/issue", json=payload)
        r.raise_for_status()
        data = r.json()
        return {"result": {"key": data["key"], "url": f"{JIRA_URL}/browse/{data['key']}"}}


async def search_issues(jql: str, max_results: int = 20):
    async with jira_client() as client:
        r = await client.get("/rest/api/3/search", params={"jql": jql, "maxResults": max_results, "fields": "summary,status,assignee,priority"})
        r.raise_for_status()
        issues = r.json().get("issues", [])
        return {"result": [{"key": i["key"], "summary": i["fields"]["summary"], "status": i["fields"]["status"]["name"]} for i in issues]}


async def get_issue(issue_key: str):
    async with jira_client() as client:
        r = await client.get(f"/rest/api/3/issue/{issue_key}")
        r.raise_for_status()
        data = r.json()
        return {"result": {"key": data["key"], "summary": data["fields"]["summary"], "status": data["fields"]["status"]["name"], "priority": data["fields"]["priority"]["name"]}}


async def update_issue(issue_key: str, status: str = None, summary: str = None):
    async with jira_client() as client:
        if summary:
            await client.put(f"/rest/api/3/issue/{issue_key}", json={"fields": {"summary": summary}})
        if status:
            transitions = await client.get(f"/rest/api/3/issue/{issue_key}/transitions")
            for t in transitions.json().get("transitions", []):
                if t["name"].lower() == status.lower():
                    await client.post(f"/rest/api/3/issue/{issue_key}/transitions", json={"transition": {"id": t["id"]}})
                    break
        return {"result": f"Issue {issue_key} updated."}


async def add_comment(issue_key: str, comment: str):
    async with jira_client() as client:
        payload = {"body": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]}}
        r = await client.post(f"/rest/api/3/issue/{issue_key}/comment", json=payload)
        r.raise_for_status()
        return {"result": f"Comment added to {issue_key}."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8101)
