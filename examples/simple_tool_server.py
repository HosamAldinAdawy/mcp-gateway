"""
Simple example MCP server — use this as a template for your own tools.
Run: python examples/simple_tool_server.py
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any
import uvicorn

app = FastAPI(title="Echo MCP Server")


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/call")
def call(req: CallRequest):
    if req.tool == "echo":
        message = req.arguments.get("message", "")
        return {"result": f"Echo: {message}"}
    return {"error": f"Unknown tool: {req.tool}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
