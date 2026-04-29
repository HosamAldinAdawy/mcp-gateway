"""
MCP Gateway Template — Xray Server
Xray test management for Jira: test cases, executions, test plans.

Setup:
  pip install fastapi uvicorn httpx
  export JIRA_URL=https://yourcompany.atlassian.net
  export XRAY_CLIENT_ID=your-client-id
  export XRAY_CLIENT_SECRET=your-client-secret
  python templates/qa/xray_server.py
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Xray MCP Server")

JIRA_URL      = os.getenv("JIRA_URL", "")
CLIENT_ID     = os.getenv("XRAY_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("XRAY_CLIENT_SECRET", "")
XRAY_BASE     = "https://xray.cloud.getxray.app/api/v2"

_token_cache = {"token": None}


async def get_token():
    if _token_cache["token"]:
        return _token_cache["token"]
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{XRAY_BASE}/authenticate",
                         json={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET})
        r.raise_for_status()
        _token_cache["token"] = r.json()
        return _token_cache["token"]


def xray_client(token):
    return httpx.AsyncClient(
        base_url=XRAY_BASE,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=15.0,
    )


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "xray"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        token = await get_token()
        if req.tool == "get_test":
            return await get_test(token, **req.arguments)
        elif req.tool == "create_test":
            return await create_test(token, **req.arguments)
        elif req.tool == "get_test_plan":
            return await get_test_plan(token, **req.arguments)
        elif req.tool == "create_test_execution":
            return await create_test_execution(token, **req.arguments)
        elif req.tool == "update_test_run":
            return await update_test_run(token, **req.arguments)
        elif req.tool == "import_results":
            return await import_results(token, **req.arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def get_test(token, test_issue_id: str):
    async with xray_client(token) as c:
        r = await c.get(f"/tests/{test_issue_id}")
        r.raise_for_status()
        return r.json()


async def create_test(token, summary: str, project_key: str, test_type: str = "Manual",
                      steps: list = None, description: str = ""):
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Test"},
        },
        "xray_fields": {"test_type": {"name": test_type}},
    }
    if steps:
        payload["xray_fields"]["steps"] = steps
    async with xray_client(token) as c:
        r = await c.post("/tests", json=payload)
        r.raise_for_status()
        return r.json()


async def get_test_plan(token, plan_id: str):
    async with xray_client(token) as c:
        r = await c.get(f"/testplans/{plan_id}")
        r.raise_for_status()
        return r.json()


async def create_test_execution(token, summary: str, project_key: str, test_keys: list):
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": "Test Execution"},
        },
        "tests": test_keys,
    }
    async with xray_client(token) as c:
        r = await c.post("/testexecutions", json=payload)
        r.raise_for_status()
        return r.json()


async def update_test_run(token, run_id: str, status: str, comment: str = ""):
    payload = {"status": status, "comment": comment}
    async with xray_client(token) as c:
        r = await c.put(f"/testruns/{run_id}", json=payload)
        r.raise_for_status()
        return r.json()


async def import_results(token, format: str, results: dict):
    endpoint = {
        "junit":   "/import/execution/junit",
        "cucumber":"/import/execution/cucumber",
        "nunit":   "/import/execution/nunit",
        "xunit":   "/import/execution/xunit",
    }.get(format, "/import/execution/junit")
    async with xray_client(token) as c:
        r = await c.post(endpoint, json=results)
        r.raise_for_status()
        return r.json()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8106)
