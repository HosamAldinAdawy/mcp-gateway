"""
MCP Gateway Template — Linear Server
Manage Linear issues, projects, and cycles.

Setup:
  pip install fastapi uvicorn httpx
  export LINEAR_API_KEY=your-linear-api-key
  python templates/dev/linear_server.py
"""
import os
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Linear MCP Server")

API_KEY  = os.getenv("LINEAR_API_KEY", "")
GQL_URL  = "https://api.linear.app/graphql"


def client():
    return httpx.AsyncClient(
        headers={"Authorization": API_KEY, "Content-Type": "application/json"},
        timeout=15.0,
    )


async def gql(query: str, variables: dict = None):
    async with client() as c:
        r = await c.post(GQL_URL, json={"query": query, "variables": variables or {}})
        r.raise_for_status()
        data = r.json()
        if "errors" in data:
            raise Exception(str(data["errors"]))
        return data.get("data", {})


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "linear"}


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
        elif req.tool == "list_teams":
            return await list_teams()
        elif req.tool == "list_projects":
            return await list_projects(**req.arguments)
        elif req.tool == "get_cycles":
            return await get_cycles(**req.arguments)
        elif req.tool == "add_comment":
            return await add_comment(**req.arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def create_issue(title: str, team_id: str, description: str = "",
                       priority: int = 0, label_ids: list = None):
    mutation = """
    mutation CreateIssue($input: IssueCreateInput!) {
      issueCreate(input: $input) { success issue { id identifier title url } }
    }"""
    inp = {"title": title, "teamId": team_id, "description": description, "priority": priority}
    if label_ids:
        inp["labelIds"] = label_ids
    data = await gql(mutation, {"input": inp})
    return data.get("issueCreate", {}).get("issue", {})


async def search_issues(query: str, team_id: str = "", limit: int = 20):
    q = """
    query SearchIssues($filter: IssueFilter, $first: Int) {
      issues(filter: $filter, first: $first) {
        nodes { id identifier title state { name } priority assignee { name } url }
      }
    }"""
    filt = {"title": {"containsIgnoreCase": query}}
    if team_id:
        filt["team"] = {"id": {"eq": team_id}}
    data = await gql(q, {"filter": filt, "first": limit})
    return {"issues": data.get("issues", {}).get("nodes", [])}


async def get_issue(issue_id: str):
    q = """
    query GetIssue($id: String!) {
      issue(id: $id) {
        id identifier title description state { name }
        priority assignee { name } labels { nodes { name } }
        createdAt updatedAt url
      }
    }"""
    data = await gql(q, {"id": issue_id})
    return data.get("issue", {})


async def update_issue(issue_id: str, title: str = None, state_id: str = None,
                       priority: int = None, description: str = None):
    mutation = """
    mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) { success issue { id identifier title } }
    }"""
    inp = {}
    if title:       inp["title"]       = title
    if state_id:    inp["stateId"]     = state_id
    if priority is not None: inp["priority"] = priority
    if description: inp["description"] = description
    data = await gql(mutation, {"id": issue_id, "input": inp})
    return data.get("issueUpdate", {})


async def list_teams():
    q = "{ teams { nodes { id name key } } }"
    data = await gql(q)
    return {"teams": data.get("teams", {}).get("nodes", [])}


async def list_projects(team_id: str = ""):
    q = """
    query ListProjects($filter: ProjectFilter) {
      projects(filter: $filter) { nodes { id name state } }
    }"""
    filt = {}
    if team_id:
        filt = {"members": {"some": {"team": {"id": {"eq": team_id}}}}}
    data = await gql(q, {"filter": filt})
    return {"projects": data.get("projects", {}).get("nodes", [])}


async def get_cycles(team_id: str):
    q = """
    query GetCycles($teamId: String!) {
      team(id: $teamId) {
        cycles { nodes { id name number startsAt endsAt completedAt } }
      }
    }"""
    data = await gql(q, {"teamId": team_id})
    return {"cycles": data.get("team", {}).get("cycles", {}).get("nodes", [])}


async def add_comment(issue_id: str, body: str):
    mutation = """
    mutation AddComment($input: CommentCreateInput!) {
      commentCreate(input: $input) { success comment { id body createdAt } }
    }"""
    data = await gql(mutation, {"input": {"issueId": issue_id, "body": body}})
    return data.get("commentCreate", {})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8206)
