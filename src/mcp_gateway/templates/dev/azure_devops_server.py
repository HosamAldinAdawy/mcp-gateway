"""
MCP Gateway Template — Azure DevOps Server
Manage work items, pipelines, and test plans.

Setup:
  pip install fastapi uvicorn httpx
  export AZURE_DEVOPS_ORG=your-org
  export AZURE_DEVOPS_TOKEN=your-pat
  export AZURE_DEVOPS_PROJECT=your-project
  python templates/dev/azure_devops_server.py
"""
import os
import base64
import httpx
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Azure DevOps MCP Server")

ORG = os.getenv("AZURE_DEVOPS_ORG", "")
TOKEN = os.getenv("AZURE_DEVOPS_TOKEN", "")
PROJECT = os.getenv("AZURE_DEVOPS_PROJECT", "")
B64_TOKEN = base64.b64encode(f":{TOKEN}".encode()).decode()


def az_client(api: str = ""):
    base = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis" if not api else f"https://{api}.dev.azure.com/{ORG}/{PROJECT}/_apis"
    return httpx.AsyncClient(
        base_url=base,
        headers={"Authorization": f"Basic {B64_TOKEN}", "Content-Type": "application/json"},
        timeout=15.0,
    )


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "azure-devops"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        tools = {
            "create_work_item": create_work_item,
            "get_work_item": get_work_item,
            "get_pipeline": get_pipeline,
            "run_pipeline": run_pipeline,
            "get_test_plan": get_test_plan,
        }
        if req.tool not in tools:
            return {"error": f"Unknown tool: {req.tool}"}
        return await tools[req.tool](**req.arguments)
    except Exception as e:
        return {"error": str(e)}


async def create_work_item(title: str, work_item_type: str = "Bug", description: str = "", priority: int = 2):
    patch = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/System.Description", "value": description},
        {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": priority},
    ]
    async with az_client() as client:
        r = await client.post(
            f"/wit/workitems/${work_item_type}?api-version=7.0",
            content=__import__("json").dumps(patch),
            headers={"Content-Type": "application/json-patch+json"},
        )
        r.raise_for_status()
        data = r.json()
        return {"result": {"id": data["id"], "title": title, "url": data["_links"]["html"]["href"]}}


async def get_work_item(item_id: int):
    async with az_client() as client:
        r = await client.get(f"/wit/workitems/{item_id}?api-version=7.0")
        r.raise_for_status()
        data = r.json()
        fields = data["fields"]
        return {"result": {"id": data["id"], "title": fields.get("System.Title"), "state": fields.get("System.State"), "type": fields.get("System.WorkItemType")}}


async def get_pipeline(pipeline_id: int):
    async with az_client() as client:
        r = await client.get(f"/pipelines/{pipeline_id}?api-version=7.0")
        r.raise_for_status()
        data = r.json()
        return {"result": {"id": data["id"], "name": data["name"], "folder": data.get("folder", "")}}


async def run_pipeline(pipeline_id: int, branch: str = "main"):
    async with az_client() as client:
        r = await client.post(
            f"/pipelines/{pipeline_id}/runs?api-version=7.0",
            json={"resources": {"repositories": {"self": {"refName": f"refs/heads/{branch}"}}}}
        )
        r.raise_for_status()
        data = r.json()
        return {"result": {"run_id": data["id"], "state": data["state"], "url": data["_links"]["web"]["href"]}}


async def get_test_plan(plan_id: int):
    async with az_client("vstmr") as client:
        r = await client.get(f"/testplan/plans/{plan_id}?api-version=7.0")
        r.raise_for_status()
        data = r.json()
        return {"result": {"id": data["id"], "name": data["name"], "state": data.get("state")}}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("AZURE_PORT", "8203")))
