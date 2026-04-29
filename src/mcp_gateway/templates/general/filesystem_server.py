"""
MCP Gateway Template — Filesystem Server
Read, write, search files safely.

Setup:
  pip install fastapi uvicorn
  export FS_ROOT=/path/to/allowed/directory
  python templates/general/filesystem_server.py
"""
import os
import uvicorn
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Filesystem MCP Server")

FS_ROOT = Path(os.getenv("FS_ROOT", str(Path.home() / "mcp-files")))
FS_ROOT.mkdir(parents=True, exist_ok=True)


def safe_path(relative: str) -> Path:
    target = (FS_ROOT / relative).resolve()
    if not str(target).startswith(str(FS_ROOT)):
        raise HTTPException(status_code=403, detail="Access outside root is not allowed.")
    return target


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "filesystem", "root": str(FS_ROOT)}


@app.post("/call")
async def call(req: CallRequest):
    try:
        tools = {
            "read_file": read_file,
            "write_file": write_file,
            "search_files": search_files,
            "list_dir": list_dir,
            "delete_file": delete_file,
        }
        if req.tool not in tools:
            return {"error": f"Unknown tool: {req.tool}"}
        return tools[req.tool](**req.arguments)
    except HTTPException as e:
        return {"error": e.detail}
    except Exception as e:
        return {"error": str(e)}


def read_file(path: str):
    p = safe_path(path)
    if not p.exists():
        return {"error": f"File not found: {path}"}
    return {"result": p.read_text(errors="replace")}


def write_file(path: str, content: str):
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return {"result": f"Written {len(content)} chars to {path}"}


def search_files(pattern: str, directory: str = "."):
    root = safe_path(directory)
    matches = list(root.rglob(pattern))[:50]
    return {"result": [str(m.relative_to(FS_ROOT)) for m in matches]}


def list_dir(path: str = "."):
    p = safe_path(path)
    if not p.is_dir():
        return {"error": f"Not a directory: {path}"}
    items = []
    for item in sorted(p.iterdir()):
        items.append({"name": item.name, "type": "dir" if item.is_dir() else "file", "size": item.stat().st_size if item.is_file() else None})
    return {"result": items}


def delete_file(path: str):
    p = safe_path(path)
    if not p.exists():
        return {"error": f"File not found: {path}"}
    p.unlink()
    return {"result": f"Deleted: {path}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8301)
