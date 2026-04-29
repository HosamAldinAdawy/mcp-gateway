# استخدام MCP Gateway مع Python

## التثبيت

```bash
pip install httpx
```

## مثال بسيط

```python
import httpx

GATEWAY_URL = "http://localhost:8000/v1"
API_KEY = "your-api-key-here"

def call_tool(server: str, tool: str, arguments: dict):
    response = httpx.post(
        f"{GATEWAY_URL}/call",
        headers={"X-API-Key": API_KEY},
        json={"server": server, "tool": tool, "arguments": arguments},
    )
    return response.json()

# إنشاء Jira bug
result = call_tool(
    server="jira",
    tool="create_issue",
    arguments={
        "project": "QA",
        "summary": "Login button not working on mobile",
        "issue_type": "Bug",
        "priority": "High",
    }
)
print(result)

# تشغيل pytest
result = call_tool(
    server="pytest-runner",
    tool="run_tests",
    arguments={"path": "tests/", "markers": "smoke"}
)
print(f"Passed: {result['result']['passed']}, Failed: {result['result']['failed']}")
```

## مثال مع async

```python
import asyncio
import httpx

async def call_tool_async(server: str, tool: str, arguments: dict):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "http://localhost:8000/v1/call",
            headers={"X-API-Key": "your-api-key-here"},
            json={"server": server, "tool": tool, "arguments": arguments},
        )
        return r.json()

async def main():
    result = await call_tool_async("github", "list_prs", {"owner": "myorg", "repo": "myrepo"})
    print(result)

asyncio.run(main())
```
