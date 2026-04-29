"""
MCP Gateway Template — Git Local Server
Run git operations on local repositories.

Setup:
  pip install fastapi uvicorn
  python templates/dev/git_server.py
"""
import os
import subprocess
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Git Local MCP Server")


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


def run_git(repo_path: str, *args) -> dict:
    try:
        result = subprocess.run(
            ["git", "-C", repo_path] + list(args),
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip()}
        return {"result": result.stdout.strip()}
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
def health():
    return {"status": "ok", "server": "git-local"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        tools = {
            "status": git_status,
            "diff": git_diff,
            "commit": git_commit,
            "log": git_log,
            "branch": git_branch,
            "checkout": git_checkout,
        }
        if req.tool not in tools:
            return {"error": f"Unknown tool: {req.tool}"}
        return tools[req.tool](**req.arguments)
    except Exception as e:
        return {"error": str(e)}


def git_status(repo_path: str):
    return run_git(repo_path, "status", "--short")


def git_diff(repo_path: str, file: str = None):
    args = ["diff"]
    if file:
        args.append(file)
    return run_git(repo_path, *args)


def git_commit(repo_path: str, message: str, add_all: bool = False):
    if add_all:
        run_git(repo_path, "add", "-A")
    return run_git(repo_path, "commit", "-m", message)


def git_log(repo_path: str, limit: int = 10):
    result = run_git(repo_path, "log", f"--max-count={limit}", "--oneline")
    if "error" in result:
        return result
    lines = result["result"].split("\n")
    return {"result": [{"sha": l[:7], "message": l[8:]} for l in lines if l]}


def git_branch(repo_path: str):
    return run_git(repo_path, "branch", "-a")


def git_checkout(repo_path: str, branch: str, create: bool = False):
    args = ["checkout"]
    if create:
        args.append("-b")
    args.append(branch)
    return run_git(repo_path, *args)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("GIT_PORT", "8202")))
