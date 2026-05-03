"""
MCP Gateway — Embedded Server Manager
Automatically starts MCP servers based on credentials in .env
"""
import os
import threading
import logging
from pathlib import Path

log = logging.getLogger("server_manager")


def _run_server(app, port: int, name: str):
    """Run a FastAPI app on a given port in a background thread."""
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
    except Exception as e:
        log.warning(f"[{name}] server failed: {e}")


def _start(app, port: int, name: str):
    t = threading.Thread(target=_run_server, args=(app, port, name), daemon=True)
    t.start()
    log.info(f"[{name}] started on :{port}")


def start_all():
    """
    Check .env and start every server whose credentials are present.
    Each server runs on a fixed port in a daemon thread.
    """
    started = []

    # ── Jira ─────────────────────────────────────────────────────────────────
    if os.getenv("JIRA_URL") and os.getenv("JIRA_TOKEN") and os.getenv("JIRA_EMAIL"):
        try:
            from templates.qa.jira_server import app as jira_app
            _start(jira_app, 8101, "jira")
            started.append("jira")
        except Exception as e:
            log.warning(f"[jira] failed to import: {e}")

    # ── TestRail ──────────────────────────────────────────────────────────────
    if os.getenv("TESTRAIL_URL") and os.getenv("TESTRAIL_KEY") and os.getenv("TESTRAIL_USER"):
        try:
            from templates.qa.testrail_server import app as testrail_app
            _start(testrail_app, 8102, "testrail")
            started.append("testrail")
        except Exception as e:
            log.warning(f"[testrail] failed to import: {e}")

    # ── Pytest ────────────────────────────────────────────────────────────────
    if os.getenv("PLAYWRIGHT_PROJECT_PATH") or Path(".").exists():
        try:
            from templates.qa.pytest_server import app as pytest_app
            _start(pytest_app, 8103, "pytest-runner")
            started.append("pytest-runner")
        except Exception as e:
            log.warning(f"[pytest] failed to import: {e}")

    # ── Xray ──────────────────────────────────────────────────────────────────
    if os.getenv("XRAY_CLIENT_ID") and os.getenv("XRAY_CLIENT_SECRET"):
        try:
            from templates.qa.xray_server import app as xray_app
            _start(xray_app, 8106, "xray")
            started.append("xray")
        except Exception as e:
            log.warning(f"[xray] failed to import: {e}")

    # ── Playwright ────────────────────────────────────────────────────────────
    if os.getenv("PLAYWRIGHT_PROJECT_PATH"):
        try:
            from templates.qa.playwright_server import app as pw_app
            _start(pw_app, 8107, "playwright")
            started.append("playwright")
        except Exception as e:
            log.warning(f"[playwright] failed to import: {e}")

    # ── Allure ────────────────────────────────────────────────────────────────
    if os.getenv("ALLURE_RESULTS_DIR"):
        try:
            from templates.qa.allure_server import app as allure_app
            _start(allure_app, 8108, "allure")
            started.append("allure")
        except Exception as e:
            log.warning(f"[allure] failed to import: {e}")

    # ── Selenium ──────────────────────────────────────────────────────────────
    try:
        from templates.qa.selenium_server import app as selenium_app
        _start(selenium_app, 8110, "selenium")
        started.append("selenium")
    except Exception as e:
        log.warning(f"[selenium] failed to import: {e}")

    # ── GitHub ────────────────────────────────────────────────────────────────
    if os.getenv("GITHUB_TOKEN"):
        try:
            from templates.dev.github_server import app as github_app
            _start(github_app, 8201, "github")
            started.append("github")
        except Exception as e:
            log.warning(f"[github] failed to import: {e}")

    # ── Git local ─────────────────────────────────────────────────────────────
    try:
        from templates.dev.git_server import app as git_app
        _start(git_app, 8202, "git-local")
        started.append("git-local")
    except Exception as e:
        log.warning(f"[git-local] failed to import: {e}")

    # ── Azure DevOps ──────────────────────────────────────────────────────────
    if os.getenv("AZURE_TOKEN") and os.getenv("AZURE_ORG"):
        try:
            from templates.dev.azure_devops_server import app as azure_app
            _start(azure_app, 8203, "azure-devops")
            started.append("azure-devops")
        except Exception as e:
            log.warning(f"[azure] failed to import: {e}")

    # ── Code Runner ───────────────────────────────────────────────────────────
    try:
        from templates.dev.code_runner_server import app as code_app
        _start(code_app, 8204, "code-runner")
        started.append("code-runner")
    except Exception as e:
        log.warning(f"[code-runner] failed to import: {e}")

    # ── Confluence ────────────────────────────────────────────────────────────
    if os.getenv("CONFLUENCE_URL") and os.getenv("CONFLUENCE_TOKEN"):
        try:
            from templates.dev.confluence_server import app as confluence_app
            _start(confluence_app, 8205, "confluence")
            started.append("confluence")
        except Exception as e:
            log.warning(f"[confluence] failed to import: {e}")

    # ── Linear ────────────────────────────────────────────────────────────────
    if os.getenv("LINEAR_API_KEY"):
        try:
            from templates.dev.linear_server import app as linear_app
            _start(linear_app, 8206, "linear")
            started.append("linear")
        except Exception as e:
            log.warning(f"[linear] failed to import: {e}")

    # ── GitLab ────────────────────────────────────────────────────────────────
    if os.getenv("GITLAB_TOKEN"):
        try:
            from templates.dev.gitlab_server import app as gitlab_app
            _start(gitlab_app, 8207, "gitlab")
            started.append("gitlab")
        except Exception as e:
            log.warning(f"[gitlab] failed to import: {e}")

    # ── Slack ─────────────────────────────────────────────────────────────────
    if os.getenv("SLACK_TOKEN"):
        try:
            from templates.general.slack_server import app as slack_app
            _start(slack_app, 8301, "slack")
            started.append("slack")
        except Exception as e:
            log.warning(f"[slack] failed to import: {e}")

    # ── Notion ────────────────────────────────────────────────────────────────
    if os.getenv("NOTION_TOKEN"):
        try:
            from templates.general.notion_server import app as notion_app
            _start(notion_app, 8307, "notion")
            started.append("notion")
        except Exception as e:
            log.warning(f"[notion] failed to import: {e}")

    # ── Asana ─────────────────────────────────────────────────────────────────
    if os.getenv("ASANA_TOKEN"):
        try:
            from templates.general.asana_server import app as asana_app
            _start(asana_app, 8308, "asana")
            started.append("asana")
        except Exception as e:
            log.warning(f"[asana] failed to import: {e}")

    # ── Google Sheets ─────────────────────────────────────────────────────────
    if os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"):
        try:
            from templates.general.google_sheets_server import app as sheets_app
            _start(sheets_app, 8309, "google-sheets")
            started.append("google-sheets")
        except Exception as e:
            log.warning(f"[google-sheets] failed to import: {e}")

    # ── Figma ─────────────────────────────────────────────────────────────────
    if os.getenv("FIGMA_TOKEN"):
        try:
            from templates.general.figma_server import app as figma_app
            _start(figma_app, 8310, "figma")
            started.append("figma")
        except Exception as e:
            log.warning(f"[figma] failed to import: {e}")

    # ── Filesystem ────────────────────────────────────────────────────────────
    try:
        from templates.general.filesystem_server import app as fs_app
        _start(fs_app, 8302, "filesystem")
        started.append("filesystem")
    except Exception as e:
        log.warning(f"[filesystem] failed to import: {e}")

    # ── REST API ──────────────────────────────────────────────────────────────
    if os.getenv("REST_API_BASE_URL") or True:  # always available
        try:
            from templates.general.rest_api_server import app as rest_app
            _start(rest_app, 8303, "rest-api")
            started.append("rest-api")
        except Exception as e:
            log.warning(f"[rest-api] failed to import: {e}")

    # ── Web Search ────────────────────────────────────────────────────────────
    try:
        from templates.general.web_search_server import app as ws_app
        _start(ws_app, 8304, "web-search")
        started.append("web-search")
    except Exception as e:
        log.warning(f"[web-search] failed to import: {e}")

    # ── Database ──────────────────────────────────────────────────────────────
    if os.getenv("DATABASE_URL"):
        try:
            from templates.general.database_server import app as db_app
            _start(db_app, 8305, "database")
            started.append("database")
        except Exception as e:
            log.warning(f"[database] failed to import: {e}")

    print(f"\n[server_manager] Started {len(started)} embedded servers: {', '.join(started) if started else 'none'}")
    return started
