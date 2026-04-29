"""
MCP Gateway Template — Allure Server
Generate and read Allure test reports.

Setup:
  pip install fastapi uvicorn
  npm install -g allure-commandline
  export ALLURE_RESULTS_DIR=/path/to/allure-results
  export ALLURE_REPORT_DIR=/path/to/allure-report
  python templates/qa/allure_server.py
"""
import os
import json
import subprocess
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
from pathlib import Path

app = FastAPI(title="Allure MCP Server")

RESULTS_DIR = os.getenv("ALLURE_RESULTS_DIR", "./allure-results")
REPORT_DIR  = os.getenv("ALLURE_REPORT_DIR", "./allure-report")


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "allure"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        if req.tool == "generate_report":
            return await generate_report()
        elif req.tool == "get_summary":
            return await get_summary()
        elif req.tool == "get_failures":
            return await get_failures(**req.arguments)
        elif req.tool == "get_flaky_tests":
            return await get_flaky_tests()
        elif req.tool == "get_test_details":
            return await get_test_details(**req.arguments)
        elif req.tool == "get_trends":
            return await get_trends()
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_report():
    result = subprocess.run(
        ["allure", "generate", RESULTS_DIR, "--output", REPORT_DIR, "--clean"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        return {"error": result.stderr, "returncode": result.returncode}
    return {"success": True, "report_path": REPORT_DIR, "message": "Report generated"}


async def get_summary():
    summary_path = Path(REPORT_DIR) / "widgets" / "summary.json"
    if not summary_path.exists():
        return {"error": "Report not found. Run generate_report first."}
    with open(summary_path) as f:
        data = json.load(f)
    stats = data.get("statistic", {})
    return {
        "total":   stats.get("total", 0),
        "passed":  stats.get("passed", 0),
        "failed":  stats.get("failed", 0),
        "broken":  stats.get("broken", 0),
        "skipped": stats.get("skipped", 0),
        "pass_rate": round(stats.get("passed", 0) / max(stats.get("total", 1), 1) * 100, 1),
        "duration_ms": data.get("time", {}).get("duration", 0),
    }


async def get_failures(limit: int = 20):
    path = Path(REPORT_DIR) / "data" / "test-cases"
    if not path.exists():
        return {"error": "Report not found. Run generate_report first."}
    failures = []
    for f in sorted(path.glob("*.json"))[:200]:
        with open(f) as fh:
            tc = json.load(fh)
        if tc.get("status") in ("failed", "broken"):
            failures.append({
                "name":       tc.get("name"),
                "status":     tc.get("status"),
                "duration_ms":tc.get("time", {}).get("duration", 0),
                "message":    tc.get("statusMessage", ""),
                "trace":      tc.get("statusTrace", "")[:300],
            })
    return {"failures": failures[:limit], "total_failures": len(failures)}


async def get_flaky_tests():
    path = Path(REPORT_DIR) / "widgets" / "summary.json"
    if not path.exists():
        return {"error": "Report not found. Run generate_report first."}
    cases_path = Path(REPORT_DIR) / "data" / "test-cases"
    flaky = []
    for f in cases_path.glob("*.json"):
        with open(f) as fh:
            tc = json.load(fh)
        if tc.get("flaky"):
            flaky.append({"name": tc.get("name"), "retriesCount": tc.get("retriesCount", 0)})
    return {"flaky_tests": flaky, "total": len(flaky)}


async def get_test_details(test_name: str):
    cases_path = Path(REPORT_DIR) / "data" / "test-cases"
    for f in cases_path.glob("*.json"):
        with open(f) as fh:
            tc = json.load(fh)
        if test_name.lower() in tc.get("name", "").lower():
            return tc
    return {"error": f"Test '{test_name}' not found in report"}


async def get_trends():
    path = Path(REPORT_DIR) / "widgets" / "history-trend.json"
    if not path.exists():
        return {"error": "No trend data found. Need multiple report runs."}
    with open(path) as f:
        return {"trends": json.load(f)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8108)
