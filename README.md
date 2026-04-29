# MCP Gateway

> Secure local MCP gateway — auth, audit, registry, and 22 ready-made templates.
> Double-click to start. No terminal needed.

---

## The Problem

Companies don't trust remote MCP servers. Not because the code is bad — because there's no auth standard, no visibility into what happens, and no way to control which servers are allowed.

So everyone runs everything locally with zero security layer.

## The Solution

MCP Gateway sits between your LLM and your MCP servers. Every tool call passes through it. Nothing runs unless it's in the registry.

```
Claude / Cursor / Any LLM
         |
    MCP Gateway
  (Auth + Registry + Audit + Policy)
         |
  Jira | GitHub | Pytest | Notion | Slack | ...
```

---

## Start in 60 Seconds

### Option 1 — Desktop App (Recommended)

1. Download `mcp-gateway.exe` (Windows) or `mcp-gateway-mac.zip` (Mac) from [Releases](../../releases)
2. Double-click — browser opens automatically at `localhost:8000`
3. Click **"Generate a new key"** → follow the 3 steps → connect
4. Go to **Quick Setup** → pick a template → fill credentials → copy config to Cursor

Done.

### Option 2 — pip install

```bash
pip install mcp-gateway
mcp-gateway init    # creates .env in current folder
mcp-gateway start   # starts on :8000
```

### Option 3 — from source

```bash
git clone https://github.com/HosamAldinAdawy/mcp-gateway.git
cd mcp-gateway
pip install -r requirements.txt
make run
```

---

## Templates — 22 Ready to Use

### QA Tools
| Template | Tools |
|---|---|
| **Jira** | create_issue, search_issues, update_issue, get_issue, add_comment |
| **TestRail** | get_test_cases, create_test_case, add_result, create_run |
| **Xray** | get_test, create_test, get_test_plan, create_test_execution, update_test_run, import_results |
| **Pytest** | run_tests, run_suite, get_coverage |
| **Playwright** | run_tests, run_test_file, run_test_by_name, get_last_report, screenshot_url, list_tests |
| **Allure** | generate_report, get_summary, get_failures, get_flaky_tests, get_trends |

### Dev Tools
| Template | Tools |
|---|---|
| **GitHub** | create_issue, list_prs, merge_pr, create_branch, get_commits |
| **GitLab** | create_issue, list_issues, create_merge_request, list_pipelines, trigger_pipeline, get_commits |
| **Git Local** | status, diff, commit, log, branch, checkout |
| **Azure DevOps** | create_work_item, get_pipeline, run_pipeline, get_test_plan |
| **Confluence** | get_page, search_pages, create_page, update_page, list_spaces |
| **Linear** | create_issue, search_issues, update_issue, list_teams, get_cycles, add_comment |
| **Code Runner** | run_python, run_shell, run_javascript |

### General Tools
| Template | Tools |
|---|---|
| **Slack** | send_message, list_channels, get_messages, create_channel |
| **Notion** | get_page, search, create_page, update_page, query_database |
| **Asana** | create_task, update_task, list_tasks, complete_task, add_comment |
| **Google Sheets** | read_sheet, write_row, update_cell, append_rows, get_sheet_info |
| **Figma** | get_file, get_comments, add_comment, get_components, get_image_urls |
| **Filesystem** | read_file, write_file, search_files, list_dir |
| **Database** | query, insert, update, list_tables |
| **REST API** | get, post, put, patch, delete |
| **Web Search** | search, fetch_page |

---

## Security Features

| Feature | Details |
|---|---|
| API Key Auth | Every request requires X-API-Key header |
| Registry Trust Store | Only servers in registry.json can be called |
| Audit Logging | Every call logged to logs/audit.jsonl |
| Policy Control | Control who can call which server and tool |
| Rate Limiting | 60 requests/minute per key |
| Docker Isolation | Non-root user in isolated network |

---

## Why Gateway Instead of Direct Remote MCP?

| | Direct Remote MCP | MCP Gateway |
|---|---|---|
| Credentials | Plain text on your machine | Inside gateway only |
| Audit log | None | Every call logged |
| Policy | None | Block any tool/server |
| Team sharing | Each person sets up separately | One gateway, whole team |
| Trust store | Any server connects | Only registry servers |

---

## Integrations

- [Claude Desktop](docs/with-claude-desktop.md)
- [Cursor](docs/with-cursor.md)
- [Python SDK](docs/with-python-sdk.md)

---

## Commands

```bash
mcp-gateway init          # create .env in current folder
mcp-gateway start         # start on :8000
mcp-gateway start --port 9000 --reload
mcp-gateway list          # show registered servers
mcp-gateway add --name jira --url http://localhost:8101 --tools create_issue,search_issues
mcp-gateway remove --name jira

make setup                # interactive setup wizard
make run                  # start with uvicorn
make build-exe            # build desktop executable
make logs                 # watch audit logs live
```

---

## Architecture

```
mcp-gateway/
├── launcher.py            ← desktop app entry point
├── gateway/               ← FastAPI core
├── registry/              ← trust store (registry.json)
├── security/              ← auth, audit, policy, rate limiter
├── templates/
│   ├── qa/                ← Jira, TestRail, Xray, Pytest, Playwright, Allure
│   ├── dev/               ← GitHub, GitLab, Git, Azure, Confluence, Linear
│   └── general/           ← Slack, Notion, Asana, Sheets, Figma, DB, REST
├── ui/                    ← React web UI
├── setup/wizard.py        ← interactive setup
├── docs/                  ← integration guides
└── infra/                 ← Docker setup
```

---

## License

MIT
