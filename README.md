# MCP Gateway

**Control Your MCP**

---

Every time you connect Cursor or Claude to Jira, GitHub, or any external tool — your credentials sit on your machine in plain text, and nothing monitors what happens. Any tool call goes through. Nothing is logged.

MCP Gateway fixes that. It sits between your LLM and your MCP servers. Every request passes through it, gets verified, and gets logged. Your credentials stay inside the gateway. The LLM sees only the tools.

---

## Get started in 60 seconds

### Desktop app — recommended

1. Download `mcp-gateway.exe` (Windows) or `mcp-gateway-mac.zip` (Mac) from [Releases](../../releases)
2. Double-click — the browser opens automatically
3. The UI logs you in without asking for anything
4. Go to **Quick Setup** → pick a template → fill in your credentials → copy the config to Cursor

That's it. Cursor is now talking to Jira.

### pip install

```bash
pip install mcp-gateway
mcp-gateway init
mcp-gateway start
```

### From source

```bash
git clone https://github.com/HosamAldinAdawy/mcp-gateway.git
cd mcp-gateway
pip install -r requirements.txt
make run
```

---

## The UI

On first launch, a motion logo plays and you pick your language — English, Arabic, or French. After that, the dashboard opens directly. No login screen.

There are six tabs:

**Quick Setup** — Pick a template, enter your credentials, hit "Connect & Generate config." The server starts automatically and the config is ready to paste into Cursor or Claude Desktop.

**Dashboard** — Every server has a live 🟢/🔴 health dot. Today's call stats, a tool runner, and a one-click connection test per server.

**Logs** — Full audit log with OK/Error filtering and CSV export.

**Custom Server** — Register any server you're running locally and start it with a shell command directly from the UI.

**🔑 Keys** — Add, delete, and manage API keys. Show or hide values at any time.

**⚙️ Settings** — Change the port, rate limit, CORS origins, or log level without touching `.env`. A Restart button applies changes immediately.

---

## Templates

**QA** — Jira · TestRail · Xray · Pytest · Playwright · Allure · Selenium

**Dev** — GitHub · GitLab · Git Local · Azure DevOps · Confluence · Linear · Code Runner

**General** — Slack · Notion · Asana · Google Sheets · Figma · Filesystem · Database · REST API · Web Search

---

## Why not connect directly?

|  | Without Gateway | With Gateway |
|---|---|---|
| Credentials | Stored on every machine | Inside the gateway only |
| Audit log | None | Every call recorded |
| Policy | None | Block any tool or server |
| Trust store | Any server can connect | Only registry servers |
| Rate limiting | None | 60 requests/min per key |
| Team sharing | Each person configures separately | One gateway for the whole team |

---

## Security

- **API key auth** — every request requires an `X-API-Key` header
- **Registry trust store** — only servers listed in `registry.json` can be called
- **Audit logging** — every call written to `logs/audit.jsonl` with timestamp, key, server, tool, and result
- **Policy control** — restrict which keys can call which servers and tools
- **Rate limiting** — 60 requests per minute per key by default

---

## CLI

```bash
mcp-gateway init                   # create .env in current folder
mcp-gateway start                  # start on :8000
mcp-gateway start --port 9000      # custom port
mcp-gateway list                   # list registered servers
mcp-gateway add \
  --name jira \
  --url http://localhost:8101 \
  --tools create_issue,search_issues
mcp-gateway remove --name jira
```

---

## Architecture

```
mcp-gateway/
├── launcher.py          ← desktop entry point, auto-starts servers from .env
├── gateway/             ← FastAPI core + server manager
├── registry/            ← trust store (registry.json)
├── security/            ← auth, audit, policy, rate limiter
├── templates/
│   ├── qa/              ← Jira, TestRail, Xray, Pytest, Playwright, Allure, Selenium
│   ├── dev/             ← GitHub, GitLab, Git, Azure, Confluence, Linear, Code Runner
│   └── general/         ← Slack, Notion, Asana, Sheets, Figma, Filesystem, DB, REST, Search
├── ui/                  ← React — multilingual, dark/light mode
└── infra/               ← Docker setup
```

---

## License

MIT
