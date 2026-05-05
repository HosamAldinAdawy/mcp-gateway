# MCP Gateway — Complete User Guide

> **Control Your MCP** — secure local gateway with auth, audit, registry, and 22 ready-made templates.

---

## Table of Contents

- [What is MCP Gateway?](#what-is-mcp-gateway)
- [Installation](#installation)
- [First launch](#first-launch)
- [Quick Setup — connecting your first tool](#quick-setup)
- [Dashboard](#dashboard)
- [Logs](#logs)
- [Custom Server](#custom-server)
- [Keys](#keys)
- [Settings](#settings)
- [Security model](#security-model)
- [Templates reference](#templates-reference)
- [CLI reference](#cli-reference)
- [Troubleshooting](#troubleshooting)

---

## What is MCP Gateway?

When you connect Cursor or Claude to an external tool like Jira or GitHub, the requests go directly to that tool — no verification, no logging, nothing in between. Your credentials sit in plain text, and there's no record of what happened.

MCP Gateway is a local server that sits between your LLM and your tools. Every request passes through it. Nothing runs unless it's in the registry. Every call gets logged.

```
Cursor / Claude / Any LLM
         │
    MCP Gateway
  (Auth + Registry + Audit + Policy + Rate limit)
         │
  Jira · GitHub · Slack · Notion · Pytest · ...
```

Your credentials never leave your machine. The LLM only sees the tools you expose.

---

## Installation

### Option 1 — Desktop app (recommended)

No Python required. Works on Windows and Mac out of the box.

1. Download `mcp-gateway.exe` (Windows) or `mcp-gateway-mac.zip` (Mac) from the [Releases page](../releases)
2. Double-click the file
3. The browser opens automatically at `localhost:8000`
4. The UI logs you in without asking for anything

The first time it runs, it creates a `.env` file next to the executable with a generated API key. You never need to touch it.

### Option 2 — pip install

For developers who already have Python 3.10+.

```bash
pip install mcp-gateway
mcp-gateway init    # creates .env in current folder
mcp-gateway start   # starts on :8000
```

### Option 3 — From source

```bash
git clone https://github.com/HosamAldinAdawy/mcp-gateway.git
cd mcp-gateway
pip install -r requirements.txt
make run
```

---

## First launch

On first launch, you'll see:

1. **Motion logo** — the gateway animates its logo for a few seconds
2. **Language selector** — choose English, العربية, or Français. Your choice is saved and remembered next time
3. **Dashboard** — you're in. No login screen, no API key prompt

The gateway auto-fetches the key from your `.env` and logs you in silently. You can switch language at any time using the 🌐 button in the nav bar.

---

## Quick Setup

This is where you connect a tool and get the config to paste into Cursor or Claude Desktop.

### How it works

1. Open the **Quick Setup** tab
2. Pick a template from the left panel — 22 options across QA, Dev, and General
3. Fill in your credentials on the right — API keys, URLs, tokens
4. Click **Connect & Generate config**

The gateway does three things at once:
- Saves your credentials to `.env`
- Starts the server on a fixed local port
- Generates a config block ready to paste

You'll see a green confirmation when the server is running.

### Credential fields

Sensitive fields (tokens, keys, passwords) are hidden by default. Click the 👁 icon to reveal them. Click again to hide.

### The config output

After connecting, a config block appears. Switch between **Cursor** and **Claude Desktop** tabs to get the right format.

**For Cursor** — paste into `.cursor/mcp.json` in your project folder:

```json
{
  "mcpServers": {
    "jira": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "X-API-Key": "your-key-here"
      }
    }
  }
}
```

**For Claude Desktop** — paste into:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "jira": {
      "url": "http://localhost:8000/mcp",
      "headers": {
        "X-API-Key": "your-key-here"
      }
    }
  }
}
```

Restart Cursor or Claude Desktop after updating the config.

### Connecting multiple tools

Repeat the same process for each tool. Each server starts on its own port and registers itself in the gateway. Add all your servers to the same config file:

```json
{
  "mcpServers": {
    "jira": {
      "url": "http://localhost:8000/mcp",
      "headers": { "X-API-Key": "your-key" }
    },
    "github": {
      "url": "http://localhost:8000/mcp",
      "headers": { "X-API-Key": "your-key" }
    },
    "slack": {
      "url": "http://localhost:8000/mcp",
      "headers": { "X-API-Key": "your-key" }
    }
  }
}
```

---

## Dashboard

The dashboard gives you a real-time view of everything running.

### Server list

Every registered server appears in the left sidebar with a health dot:

- 🟢 **Green** — server is online and responding
- 🔴 **Red** — server is unreachable
- ⚫ **Gray** — health status unknown (hasn't been checked yet)

Health is checked automatically every 15 seconds.

### Stats cards

Three numbers at the top of the main panel:

| Card | What it shows |
|------|---------------|
| Servers | Total servers registered in the registry |
| Healthy | Servers currently responding to health checks |
| Calls today | Total tool calls made today, pulled from the audit log |

These update every 10 seconds.

### Server details

Click any server in the sidebar to see:

- Call stats for today (total, successful, failed)
- All registered tools for that server
- The last error that occurred
- A **Test connection** button — click it to verify the server is responding right now

### Tool runner

Below the server details, you can run any tool manually:

1. Click a tool tag to select it
2. Fill in the arguments as JSON
3. Click **Run Tool**

The result appears below — green for success, red for error. Every manual run is also logged in the audit log.

---

## Logs

A full audit trail of every tool call made through the gateway.

### Stats

The top of the page shows three summary numbers for all time:

- Total calls
- Successful calls
- Failed calls

### Filtering

Use the search box to filter by server name, tool name, or API key. Use the status buttons to show only:

- **All** — everything
- **✅ OK** — successful calls only
- **❌ Err** — failed calls only

Filters combine — you can search for "jira" and filter by errors at the same time.

### Export

Click **⬇ CSV** to download all visible logs as a spreadsheet. The file includes timestamp, server, tool, success/failure, API key (first 8 characters), and error message if any.

---

## Custom Server

Register any MCP server that isn't in the template list.

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| Server name | Yes | A unique identifier — no spaces |
| Description | No | What the server does |
| Server URL | Yes | Where the server is running, e.g. `http://localhost:9001` |
| Tools | Yes | Comma-separated list of tool names the server exposes |
| Transport | Yes | `http` or `sse` |
| Start command | No | Shell command to start the server automatically |

### Start command

If you provide a start command, the gateway runs it in the background when you click **Add & Start Server**. For example:

```
python templates/qa/my_server.py
```

Leave it blank if your server is already running or you want to start it yourself.

### Requirements

Your server must expose a `POST /call` endpoint that accepts:

```json
{
  "tool": "tool_name",
  "arguments": {}
}
```

Use any file in `templates/` as a starting point.

---

## Keys

Manage all API keys from one place. Useful for teams or CI/CD pipelines where different users or systems need separate keys.

### How keys work

The gateway reads the `MCP_API_KEYS` value from `.env`. Multiple keys are supported — separate them with commas:

```
MCP_API_KEYS=key-for-team-a,key-for-ci,key-for-john
```

Any of these keys will work for authentication.

### Managing keys in the UI

The Keys tab shows all keys stored locally. For each key you can:

- **Show / hide** the value using the 👁 button
- **Copy** the key to clipboard
- **Delete** a key from local storage

> **Note:** The Keys tab manages a local list. To activate a new key on the gateway, you also need to add it to `MCP_API_KEYS` in your `.env` file (comma-separated).

### Generating a new key

Click **Generate** to create a cryptographically random key. Give it a name (e.g. "CI/CD" or "John's machine"), then click **Add Key**.

---

## Settings

Configure the gateway without opening `.env`.

### Available settings

| Setting | Default | Notes |
|---------|---------|-------|
| Port | 8000 | The port the gateway listens on |
| Rate limit / min | 60 | Max requests per minute per API key |
| CORS origins | * | Which origins can reach the gateway. Use `*` for all, or a comma-separated list |
| Log level | info | `debug` / `info` / `warning` / `error` |

### Save vs Restart

| Setting | When it applies |
|---------|----------------|
| Rate limit | Immediately after Save |
| CORS origins | Immediately after Save |
| Log level | Immediately after Save |
| Port | Only after Restart |

Click **Save Settings** to write changes to `.env`. Click **↺ Restart** to restart the gateway and apply port changes.

> ⚠️ If you change the port, you also need to update the URL in your Cursor or Claude Desktop config file (`localhost:8000` → `localhost:NEW_PORT`) and restart those tools too.

---

## Security model

Every request goes through four checks before a tool runs:

### 1. API key authentication

Every request must include a valid `X-API-Key` header. Requests without a key are rejected with `401 Unauthorized`.

### 2. Rate limiting

By default, each API key is limited to 60 requests per minute. Exceeding the limit returns `429 Too Many Requests`. Configurable in Settings.

### 3. Registry check

The requested server must exist in `registry.json` and be marked as `"trusted": true`. Requests to unknown or untrusted servers are rejected with `404 Not Found`.

### 4. Tool check

The requested tool must be in the server's tool list in the registry. Calling a tool that isn't registered returns `404 Not Found` even if the server exists.

### Audit log

Every call — successful or failed — is written to `logs/audit.jsonl`. Each entry includes:

```json
{
  "timestamp": "2025-01-01T14:32:01Z",
  "api_key": "ab12cd34",
  "server": "jira",
  "tool": "create_issue",
  "success": true,
  "error": null
}
```

---

## Templates reference

### QA tools

| Template | Port | Key credentials | Tools |
|----------|------|-----------------|-------|
| **Jira** | 8101 | `JIRA_URL`, `JIRA_EMAIL`, `JIRA_TOKEN` | create_issue, search_issues, update_issue, get_issue, add_comment |
| **TestRail** | 8102 | `TESTRAIL_URL`, `TESTRAIL_USER`, `TESTRAIL_KEY` | get_test_cases, create_test_case, add_result, create_run |
| **Xray** | 8106 | `XRAY_CLIENT_ID`, `XRAY_CLIENT_SECRET` | get_test, create_test, get_test_plan, create_test_execution, update_test_run, import_results |
| **Pytest** | 8103 | `PLAYWRIGHT_PROJECT_PATH` | run_tests, run_suite, get_coverage |
| **Playwright** | 8107 | `PLAYWRIGHT_PROJECT_PATH` | run_tests, run_test_file, run_test_by_name, get_last_report, screenshot_url, list_tests |
| **Allure** | 8108 | `ALLURE_RESULTS_DIR` | generate_report, get_summary, get_failures, get_flaky_tests, get_trends |
| **Selenium** | 8110 | `SELENIUM_BROWSER`, `SELENIUM_HEADLESS` | navigate, click, type, get_text, screenshot, execute_script, find_elements, get_page_source, back, refresh, close |

### Dev tools

| Template | Port | Key credentials | Tools |
|----------|------|-----------------|-------|
| **GitHub** | 8201 | `GITHUB_TOKEN` | create_issue, list_prs, merge_pr, create_branch, get_commits |
| **GitLab** | 8207 | `GITLAB_TOKEN`, `GITLAB_URL` | create_issue, list_issues, create_merge_request, list_pipelines, trigger_pipeline, get_commits |
| **Git Local** | 8202 | — | status, diff, commit, log, branch, checkout |
| **Azure DevOps** | 8203 | `AZURE_ORG`, `AZURE_TOKEN` | create_work_item, get_pipeline, run_pipeline, get_test_plan |
| **Confluence** | 8205 | `CONFLUENCE_URL`, `CONFLUENCE_EMAIL`, `CONFLUENCE_TOKEN` | get_page, search_pages, create_page, update_page, list_spaces |
| **Linear** | 8206 | `LINEAR_API_KEY` | create_issue, search_issues, update_issue, list_teams, get_cycles, add_comment |
| **Code Runner** | 8204 | — | run_python, run_shell, run_javascript |

### General tools

| Template | Port | Key credentials | Tools |
|----------|------|-----------------|-------|
| **Slack** | 8301 | `SLACK_TOKEN` | send_message, list_channels, get_messages, create_channel |
| **Notion** | 8307 | `NOTION_TOKEN` | get_page, search, create_page, update_page, query_database |
| **Asana** | 8308 | `ASANA_TOKEN` | create_task, update_task, list_tasks, complete_task, add_comment |
| **Google Sheets** | 8309 | `GOOGLE_SERVICE_ACCOUNT_JSON` | read_sheet, write_row, update_cell, append_rows, get_sheet_info |
| **Figma** | 8310 | `FIGMA_TOKEN` | get_file, get_comments, add_comment, get_components, get_image_urls |
| **Filesystem** | 8302 | — | read_file, write_file, search_files, list_dir |
| **Database** | 8305 | `DATABASE_URL` | query, insert, update, list_tables |
| **REST API** | 8303 | — | get, post, put, patch, delete |
| **Web Search** | 8304 | — | search, fetch_page |

---

## CLI reference

```bash
# Setup
mcp-gateway init                        # create .env in current folder
mcp-gateway start                       # start on :8000
mcp-gateway start --port 9000           # custom port
mcp-gateway start --port 9000 --reload  # with auto-reload

# Registry
mcp-gateway list                        # list all registered servers
mcp-gateway add \
  --name jira \
  --url http://localhost:8101 \
  --tools create_issue,search_issues \
  --desc "Jira issue tracking"
mcp-gateway remove --name jira

# Make commands
make run          # start with uvicorn
make build-exe    # build desktop executable
make logs         # watch audit logs live
make test         # run test suite
```

---

## Troubleshooting

### The browser shows "can't connect to localhost:8000"

The gateway isn't running. Double-click the exe again, or run `mcp-gateway start` from your project folder. Check that nothing else is using port 8000.

### Windows blocked the exe (SmartScreen warning)

Click **More info**, then **Run anyway**. The exe isn't code-signed — this is expected for open source projects. Your antivirus may also flag it; add an exclusion for the exe if needed.

### Cursor says the tool isn't available

The server isn't running or isn't in the registry. Go to Quick Setup, pick the template, and click Connect again. Check the Dashboard to confirm the server health dot is green.

### "Invalid API key" error

The key in your Cursor/Claude Desktop config doesn't match the one in `.env`. Open `.env` next to the exe and copy the value after `MCP_API_KEYS=`. Paste it into your config file.

### I changed the port and nothing works

1. Open your Cursor or Claude Desktop config file
2. Change `localhost:8000` to `localhost:NEW_PORT`
3. Save the file
4. Restart Cursor or Claude Desktop
5. Restart the gateway

### Logs show errors for every call

Check the server health dot in the Dashboard. If it's red, the underlying server isn't responding. Go to Quick Setup and reconnect the template — this will restart the server.

### The server started but the tool returns an error

The credentials may be wrong or expired. Go to Quick Setup, select the template, update the credentials, and click Connect again.

---

*MCP Gateway — MIT License — [github.com/HosamAldinAdawy/mcp-gateway](https://github.com/HosamAldinAdawy/mcp-gateway)*
