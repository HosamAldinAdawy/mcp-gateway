# ربط MCP Gateway بـ Claude Desktop

## الخطوة الأولى — شغّل الـ gateway

```bash
make run
```

## الخطوة التانية — عدّل config بتاع Claude Desktop

افتح الملف ده:

**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

وضيف الـ config ده:

```json
{
  "mcpServers": {
    "mcp-gateway": {
      "url": "http://localhost:8000/v1",
      "headers": {
        "X-API-Key": "your-api-key-here"
      }
    }
  }
}
```

## الخطوة التالتة — restart Claude Desktop

بعد الـ restart، Claude هيلاقي كل الـ tools اللي في الـ gateway تلقائي.

## جرب

قول لـ Claude:
> "ابحث عن bugs في Jira بـ status Open"

أو:
> "شغّل الـ pytest suite في مجلد tests/"
