"""
MCP Gateway Template — Playwright Server
Run Playwright browser tests, get results, take screenshots.

Setup:
  pip install fastapi uvicorn playwright
  playwright install chromium
  export PLAYWRIGHT_PROJECT_PATH=/path/to/your/tests
  python templates/qa/playwright_server.py
"""
import os
import json
import asyncio
import subprocess
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
from pathlib import Path

app = FastAPI(title="Playwright MCP Server")

PROJECT_PATH = os.getenv("PLAYWRIGHT_PROJECT_PATH", ".")


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "playwright"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        if req.tool == "run_tests":
            return await run_tests(**req.arguments)
        elif req.tool == "run_test_file":
            return await run_test_file(**req.arguments)
        elif req.tool == "run_test_by_name":
            return await run_test_by_name(**req.arguments)
        elif req.tool == "get_last_report":
            return await get_last_report()
        elif req.tool == "screenshot_url":
            return await screenshot_url(**req.arguments)
        elif req.tool == "list_tests":
            return await list_tests()
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def run_tests(browser: str = "chromium", workers: int = 1, headed: bool = False):
    cmd = ["npx", "playwright", "test", f"--project={browser}",
           f"--workers={workers}", "--reporter=json"]
    if not headed:
        cmd.append("--headless")
    result = subprocess.run(cmd, cwd=PROJECT_PATH, capture_output=True, text=True, timeout=300)
    try:
        report = json.loads(result.stdout)
        return {
            "passed": report.get("stats", {}).get("expected", 0),
            "failed": report.get("stats", {}).get("unexpected", 0),
            "skipped": report.get("stats", {}).get("skipped", 0),
            "duration_ms": report.get("stats", {}).get("duration", 0),
            "suites": [s.get("title") for s in report.get("suites", [])],
        }
    except Exception:
        return {"stdout": result.stdout[-2000:], "stderr": result.stderr[-1000:],
                "returncode": result.returncode}


async def run_test_file(file_path: str, browser: str = "chromium"):
    cmd = ["npx", "playwright", "test", file_path, f"--project={browser}", "--reporter=json"]
    result = subprocess.run(cmd, cwd=PROJECT_PATH, capture_output=True, text=True, timeout=180)
    try:
        report = json.loads(result.stdout)
        return {
            "passed": report.get("stats", {}).get("expected", 0),
            "failed": report.get("stats", {}).get("unexpected", 0),
            "failures": [
                {"title": t.get("title"), "error": t.get("results", [{}])[0].get("error", {}).get("message", "")}
                for suite in report.get("suites", [])
                for spec in suite.get("specs", [])
                for t in spec.get("tests", [])
                if t.get("results", [{}])[0].get("status") == "failed"
            ]
        }
    except Exception:
        return {"stdout": result.stdout[-2000:], "returncode": result.returncode}


async def run_test_by_name(test_name: str, browser: str = "chromium"):
    cmd = ["npx", "playwright", "test", f"--grep={test_name}",
           f"--project={browser}", "--reporter=json"]
    result = subprocess.run(cmd, cwd=PROJECT_PATH, capture_output=True, text=True, timeout=120)
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"stdout": result.stdout[-2000:], "returncode": result.returncode}


async def get_last_report():
    report_path = Path(PROJECT_PATH) / "playwright-report" / "index.html"
    json_path   = Path(PROJECT_PATH) / "test-results" / "results.json"
    if json_path.exists():
        with open(json_path) as f:
            return json.load(f)
    return {"error": "No report found. Run tests first.", "looked_at": str(json_path)}


async def screenshot_url(url: str, full_page: bool = True):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page    = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        screenshot = await page.screenshot(full_page=full_page)
        await browser.close()
        import base64
        return {"screenshot_base64": base64.b64encode(screenshot).decode(), "url": url}


async def list_tests():
    cmd = ["npx", "playwright", "test", "--list", "--reporter=json"]
    result = subprocess.run(cmd, cwd=PROJECT_PATH, capture_output=True, text=True, timeout=30)
    try:
        data = json.loads(result.stdout)
        tests = []
        for suite in data.get("suites", []):
            for spec in suite.get("specs", []):
                tests.append({"title": spec.get("title"), "file": spec.get("file")})
        return {"tests": tests, "total": len(tests)}
    except Exception:
        return {"stdout": result.stdout[-1000:]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8107)
