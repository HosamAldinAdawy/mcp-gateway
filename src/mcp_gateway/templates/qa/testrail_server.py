"""
MCP Gateway Template — TestRail Server
Manage test cases, runs, and results.

Setup:
  pip install fastapi uvicorn httpx
  export TESTRAIL_URL=https://yourcompany.testrail.io
  export TESTRAIL_EMAIL=you@company.com
  export TESTRAIL_TOKEN=your-api-key
  python templates/qa/testrail_server.py
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="TestRail MCP Server")

TESTRAIL_URL = os.getenv("TESTRAIL_URL", "")
TESTRAIL_EMAIL = os.getenv("TESTRAIL_EMAIL", "")
TESTRAIL_TOKEN = os.getenv("TESTRAIL_TOKEN", "")


def tr_client():
    return httpx.AsyncClient(
        base_url=f"{TESTRAIL_URL}/index.php?/api/v2",
        auth=(TESTRAIL_EMAIL, TESTRAIL_TOKEN),
        headers={"Content-Type": "application/json"},
        timeout=15.0,
    )


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "testrail"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        tools = {
            "get_test_cases": get_test_cases,
            "create_test_case": create_test_case,
            "add_result": add_result,
            "get_run": get_run,
            "create_run": create_run,
        }
        if req.tool not in tools:
            return {"error": f"Unknown tool: {req.tool}"}
        return await tools[req.tool](**req.arguments)
    except Exception as e:
        return {"error": str(e)}


async def get_test_cases(project_id: int, suite_id: int = None):
    async with tr_client() as client:
        url = f"/get_cases/{project_id}"
        if suite_id:
            url += f"&suite_id={suite_id}"
        r = await client.get(url)
        r.raise_for_status()
        cases = r.json().get("cases", [])
        return {"result": [{"id": c["id"], "title": c["title"], "priority": c.get("priority_id")} for c in cases[:50]]}


async def create_test_case(section_id: int, title: str, steps: str = "", expected: str = ""):
    async with tr_client() as client:
        r = await client.post(f"/add_case/{section_id}", json={
            "title": title,
            "custom_steps": steps,
            "custom_expected": expected,
        })
        r.raise_for_status()
        data = r.json()
        return {"result": {"id": data["id"], "title": data["title"]}}


async def add_result(test_id: int, status: str, comment: str = ""):
    status_map = {"passed": 1, "blocked": 2, "failed": 5, "retest": 4}
    status_id = status_map.get(status.lower(), 1)
    async with tr_client() as client:
        r = await client.post(f"/add_result/{test_id}", json={"status_id": status_id, "comment": comment})
        r.raise_for_status()
        return {"result": f"Result added for test {test_id}: {status}"}


async def get_run(run_id: int):
    async with tr_client() as client:
        r = await client.get(f"/get_run/{run_id}")
        r.raise_for_status()
        data = r.json()
        return {"result": {"id": data["id"], "name": data["name"], "passed": data["passed_count"], "failed": data["failed_count"]}}


async def create_run(project_id: int, name: str, suite_id: int = None, case_ids: list = []):
    payload = {"name": name}
    if suite_id:
        payload["suite_id"] = suite_id
    if case_ids:
        payload["case_ids"] = case_ids
    async with tr_client() as client:
        r = await client.post(f"/add_run/{project_id}", json=payload)
        r.raise_for_status()
        data = r.json()
        return {"result": {"id": data["id"], "name": data["name"], "url": data.get("url", "")}}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("TESTRAIL_PORT", "8102")))
