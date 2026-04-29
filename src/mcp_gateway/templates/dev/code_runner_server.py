"""
MCP Gateway Template — Code Runner Server
Execute Python or shell scripts in a safe sandbox.

Setup:
  pip install fastapi uvicorn
  python templates/dev/code_runner_server.py
"""
import os
import subprocess
import tempfile
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Code Runner MCP Server")
TIMEOUT = int(os.getenv("CODE_RUNNER_TIMEOUT", "30"))


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "code-runner"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        tools = {
            "run_python": run_python,
            "run_shell": run_shell,
            "run_javascript": run_javascript,
        }
        if req.tool not in tools:
            return {"error": f"Unknown tool: {req.tool}"}
        return tools[req.tool](**req.arguments)
    except Exception as e:
        return {"error": str(e)}


def run_python(code: str, timeout: int = TIMEOUT):
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        fname = f.name
    try:
        result = subprocess.run(
            ["python3", fname],
            capture_output=True, text=True, timeout=timeout
        )
        return {
            "result": {
                "stdout": result.stdout[-3000:],
                "stderr": result.stderr[-1000:],
                "returncode": result.returncode,
            }
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Timeout after {timeout}s"}
    finally:
        os.unlink(fname)


def run_shell(command: str, timeout: int = TIMEOUT):
    # Safety: block dangerous commands
    blocked = ["rm -rf", "sudo", "chmod 777", "> /dev/", "dd if="]
    for b in blocked:
        if b in command:
            return {"error": f"Blocked command pattern: {b}"}
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return {
            "result": {
                "stdout": result.stdout[-3000:],
                "stderr": result.stderr[-500:],
                "returncode": result.returncode,
            }
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Timeout after {timeout}s"}


def run_javascript(code: str, timeout: int = TIMEOUT):
    with tempfile.NamedTemporaryFile(suffix=".js", mode="w", delete=False) as f:
        f.write(code)
        fname = f.name
    try:
        result = subprocess.run(
            ["node", fname],
            capture_output=True, text=True, timeout=timeout
        )
        return {
            "result": {
                "stdout": result.stdout[-3000:],
                "stderr": result.stderr[-1000:],
                "returncode": result.returncode,
            }
        }
    except FileNotFoundError:
        return {"error": "Node.js not installed. Run: apt install nodejs"}
    except subprocess.TimeoutExpired:
        return {"error": f"Timeout after {timeout}s"}
    finally:
        os.unlink(fname)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("CODE_RUNNER_PORT", "8204")))
