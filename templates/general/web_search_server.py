"""
MCP Gateway Template — Web Search Server
Search the web in real time using DuckDuckGo (no API key needed).

Setup:
  pip install fastapi uvicorn httpx
  python templates/general/web_search_server.py
"""
import httpx
import uvicorn
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Web Search MCP Server")


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "web-search"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        tools = {
            "search": do_search,
            "fetch_page": fetch_page,
        }
        if req.tool not in tools:
            return {"error": f"Unknown tool: {req.tool}"}
        return await tools[req.tool](**req.arguments)
    except Exception as e:
        return {"error": str(e)}


async def do_search(query: str, max_results: int = 5):
    # DuckDuckGo instant answer API — no key needed
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        r = await client.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
            headers={"User-Agent": "MCP-Gateway/1.0"},
        )
        data = r.json()
        results = []
        if data.get("AbstractText"):
            results.append({"title": data.get("Heading", query), "snippet": data["AbstractText"], "url": data.get("AbstractURL", "")})
        for topic in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append({"title": topic.get("Text", "")[:80], "snippet": topic.get("Text", ""), "url": topic.get("FirstURL", "")})
        return {"result": results[:max_results]}


async def fetch_page(url: str, max_chars: int = 3000):
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        r = await client.get(url, headers={"User-Agent": "MCP-Gateway/1.0"})
        text = r.text
        # Strip HTML tags simply
        import re
        clean = re.sub(r"<[^>]+>", " ", text)
        clean = re.sub(r"\s+", " ", clean).strip()
        return {"result": clean[:max_chars]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("WEB_SEARCH_PORT", "8306")))
