"""
MCP Gateway Template — Pytest Runner
Run pytest suites and return structured results.

Setup:
  pip install fastapi uvicorn pytest pytest-json-report
  python templates/qa/pytest_server.py
"""
import json
import subprocess
import tempfile
import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Pytest Runner MCP Server")


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "pytest-runner"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        if req.tool == "run_tests":
            return await run_tests(**req.arguments)
        elif req.tool == "run_suite":
            return await run_suite(**req.arguments)
        elif req.tool == "get_coverage":
            return await get_coverage(**req.arguments)
        else:
            return {"error": f"Unknown tool: {req.tool}"}
    except Exception as e:
        return {"error": str(e)}


async def run_tests(path: str = ".", markers: str = None, keyword: str = None):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        report_file = f.name

    cmd = ["python", "-m", "pytest", path, f"--json-report", f"--json-report-file={report_file}", "-v", "--tb=short"]
    if markers:
        cmd += ["-m", markers]
    if keyword:
        cmd += ["-k", keyword]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    try:
        with open(report_file) as f:
            report = json.load(f)
        summary = report.get("summary", {})
        return {
            "result": {
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0),
                "error": summary.get("error", 0),
                "total": summary.get("total", 0),
                "duration": round(report.get("duration", 0), 2),
                "failures": [
                    {"test": t["nodeid"], "message": t.get("call", {}).get("longrepr", "")[:300]}
                    for t in report.get("tests", [])
                    if t.get("outcome") == "failed"
                ],
            }
        }
    except Exception:
        return {"result": {"stdout": result.stdout[-2000:], "returncode": result.returncode}}
    finally:
        os.unlink(report_file)


async def run_suite(suite_path: str, env: str = "test"):
    os.environ["TEST_ENV"] = env
    return await run_tests(path=suite_path)


async def get_coverage(path: str = "."):
    cmd = ["python", "-m", "pytest", path, "--cov", "--cov-report=json", "-q"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    try:
        with open("coverage.json") as f:
            cov = json.load(f)
        return {"result": {"total_coverage": cov["totals"]["percent_covered_display"], "files": {k: v["summary"]["percent_covered_display"] for k, v in cov["files"].items()}}}
    except Exception:
        return {"result": {"output": result.stdout[-1000:]}}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8105)
