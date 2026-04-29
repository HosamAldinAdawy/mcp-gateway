# ربط MCP Gateway بـ Cursor

## الخطوة الأولى — شغّل الـ gateway

```bash
make run
```

## الخطوة التانية — عدّل Cursor MCP config

افتح أو انشئ الملف:
```
~/.cursor/mcp.json
```

وضيف:

```json
{
  "mcp": {
    "servers": {
      "mcp-gateway": {
        "url": "http://localhost:8000/v1",
        "headers": {
          "X-API-Key": "your-api-key-here"
        }
      }
    }
  }
}
```

## الخطوة التالتة — restart Cursor

بعد الـ restart، هتلاقي الـ tools في الـ Cursor Agent panel.

## جرب في Cursor

```
@mcp-gateway create a Jira bug for the login issue we just found
```

أو:

```
@mcp-gateway run all pytest tests in the auth module
```
