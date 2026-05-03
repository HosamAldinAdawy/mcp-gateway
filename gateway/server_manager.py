"""
MCP Gateway — Embedded Server Manager
Automatically starts MCP servers based on credentials in .env
"""
import os
import threading
import logging
from pathlib import Path

log = logging.getLogger("server_manager")

_started = set()


def _run_server(app, port: int, name: str):
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
    except Exception as e:
        log.warning(f"[{name}] server failed: {e}")


def _start(app, port: int, name: str):
    if name in _started:
        return
    t = threading.Thread(target=_run_server, args=(app, port, name), daemon=True)
    t.start()
    _started.add(name)
    log.info(f"[{name}] started on :{port}")


def start_server(name: str) -> bool:
    """Start a single server by name. Called from /setup endpoint."""
    if name in _started:
        return True
    try:
        if name == "jira":
            from templates.qa.jira_server import app; _start(app, 8101, name)
        elif name == "testrail":
            from templates.qa.testrail_server import app; _start(app, 8102, name)
        elif name == "pytest-runner":
            from templates.qa.pytest_server import app; _start(app, 8103, name)
        elif name == "xray":
            from templates.qa.xray_server import app; _start(app, 8106, name)
        elif name == "playwright":
            from templates.qa.playwright_server import app; _start(app, 8107, name)
        elif name == "allure":
            from templates.qa.allure_server import app; _start(app, 8108, name)
        elif name == "selenium":
            from templates.qa.selenium_server import app; _start(app, 8110, name)
        elif name == "github":
            from templates.dev.github_server import app; _start(app, 8201, name)
        elif name == "git-local":
            from templates.dev.git_server import app; _start(app, 8202, name)
        elif name == "azure-devops":
            from templates.dev.azure_devops_server import app; _start(app, 8203, name)
        elif name == "code-runner":
            from templates.dev.code_runner_server import app; _start(app, 8204, name)
        elif name == "confluence":
            from templates.dev.confluence_server import app; _start(app, 8205, name)
        elif name == "linear":
            from templates.dev.linear_server import app; _start(app, 8206, name)
        elif name == "gitlab":
            from templates.dev.gitlab_server import app; _start(app, 8207, name)
        elif name == "slack":
            from templates.general.slack_server import app; _start(app, 8301, name)
        elif name == "filesystem":
            from templates.general.filesystem_server import app; _start(app, 8302, name)
        elif name == "rest-api":
            from templates.general.rest_api_server import app; _start(app, 8303, name)
        elif name == "web-search":
            from templates.general.web_search_server import app; _start(app, 8304, name)
        elif name == "notion":
            from templates.general.notion_server import app; _start(app, 8307, name)
        elif name == "asana":
            from templates.general.asana_server import app; _start(app, 8308, name)
        elif name == "google-sheets":
            from templates.general.google_sheets_server import app; _start(app, 8309, name)
        elif name == "figma":
            from templates.general.figma_server import app; _start(app, 8310, name)
        else:
            return False
        return True
    except Exception as e:
        log.warning(f"[{name}] failed to start: {e}")
        return False


def start_all():
    """Start all servers whose credentials are present in .env"""
    started = []

    if os.getenv("JIRA_URL") and os.getenv("JIRA_TOKEN") and os.getenv("JIRA_EMAIL"):
        if start_server("jira"): started.append("jira")

    if os.getenv("TESTRAIL_URL") and os.getenv("TESTRAIL_KEY") and os.getenv("TESTRAIL_USER"):
        if start_server("testrail"): started.append("testrail")

    if start_server("pytest-runner"): started.append("pytest-runner")

    if os.getenv("XRAY_CLIENT_ID") and os.getenv("XRAY_CLIENT_SECRET"):
        if start_server("xray"): started.append("xray")

    if os.getenv("PLAYWRIGHT_PROJECT_PATH"):
        if start_server("playwright"): started.append("playwright")

    if os.getenv("ALLURE_RESULTS_DIR"):
        if start_server("allure"): started.append("allure")

    if start_server("selenium"): started.append("selenium")

    if os.getenv("GITHUB_TOKEN"):
        if start_server("github"): started.append("github")

    if start_server("git-local"): started.append("git-local")

    if os.getenv("AZURE_TOKEN") and os.getenv("AZURE_ORG"):
        if start_server("azure-devops"): started.append("azure-devops")

    if start_server("code-runner"): started.append("code-runner")

    if os.getenv("CONFLUENCE_URL") and os.getenv("CONFLUENCE_TOKEN"):
        if start_server("confluence"): started.append("confluence")

    if os.getenv("LINEAR_API_KEY"):
        if start_server("linear"): started.append("linear")

    if os.getenv("GITLAB_TOKEN"):
        if start_server("gitlab"): started.append("gitlab")

    if os.getenv("SLACK_TOKEN"):
        if start_server("slack"): started.append("slack")

    if start_server("filesystem"): started.append("filesystem")
    if start_server("rest-api"):   started.append("rest-api")
    if start_server("web-search"): started.append("web-search")

    if os.getenv("NOTION_TOKEN"):
        if start_server("notion"): started.append("notion")

    if os.getenv("ASANA_TOKEN"):
        if start_server("asana"): started.append("asana")

    if os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"):
        if start_server("google-sheets"): started.append("google-sheets")

    if os.getenv("FIGMA_TOKEN"):
        if start_server("figma"): started.append("figma")

    if os.getenv("DATABASE_URL"):
        try:
            from templates.general.database_server import app as db_app
            _start(db_app, 8305, "database")
            started.append("database")
        except Exception as e:
            log.warning(f"[database] failed to import: {e}")

    print(f"\n[server_manager] Started {len(started)} embedded servers: {', '.join(started) if started else 'none'}")
    return started
