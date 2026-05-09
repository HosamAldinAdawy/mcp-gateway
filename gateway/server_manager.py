"""
MCP Gateway — Embedded Server Manager
Automatically starts MCP servers based on credentials in .env
Lazy-installs missing packages before starting servers that need them.
"""
import os
import sys
import threading
import logging
import subprocess

log = logging.getLogger("server_manager")

_started = set()


# ── Lazy package installer ────────────────────────────────────────────────────
def _ensure_packages(*packages):
    """Install packages if not already available. Returns True if all ready."""
    missing = []
    for pkg in packages:
        module = pkg.split("[")[0].replace("-", "_")
        try:
            __import__(module)
        except ImportError:
            missing.append(pkg)

    if not missing:
        return True

    # When running as frozen EXE, packages are bundled — skip install
    if getattr(sys, "frozen", False):
        return True

    print(f"\n[server_manager] Installing: {', '.join(missing)} ...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", *missing],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"[server_manager] Installed: {', '.join(missing)}")
        return True
    except Exception as e:
        log.warning(f"[server_manager] Failed to install {missing}: {e}")
        return False


# ── Server runner ─────────────────────────────────────────────────────────────
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


# ── Per-server start ──────────────────────────────────────────────────────────
def start_server(name: str) -> bool:
    """Start a single server by name. Lazy-installs dependencies if needed."""
    if name in _started:
        return True

    try:
        # ── QA ────────────────────────────────────────────────────────────────
        if name == "jira":
            from templates.qa.jira_server import app; _start(app, 8101, name)

        elif name == "testrail":
            from templates.qa.testrail_server import app; _start(app, 8102, name)

        elif name == "pytest-runner":
            from templates.qa.pytest_server import app; _start(app, 8103, name)

        elif name == "xray":
            from templates.qa.xray_server import app; _start(app, 8106, name)

        elif name == "playwright":
            if not _ensure_packages("playwright"):
                return False
            if not getattr(sys, "frozen", False):
                try:
                    subprocess.run(
                        [sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"],
                        capture_output=True, timeout=120
                    )
                except Exception:
                    pass
            from templates.qa.playwright_server import app; _start(app, 8107, name)

        elif name == "allure":
            from templates.qa.allure_server import app; _start(app, 8108, name)

        elif name == "selenium":
            if not _ensure_packages("selenium", "webdriver-manager"):
                return False
            from templates.qa.selenium_server import app; _start(app, 8110, name)

        # ── Dev ───────────────────────────────────────────────────────────────
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

        # ── General ───────────────────────────────────────────────────────────
        elif name == "slack":
            from templates.general.slack_server import app; _start(app, 8301, name)

        elif name == "filesystem":
            from templates.general.filesystem_server import app; _start(app, 8302, name)

        elif name == "rest-api":
            from templates.general.rest_api_server import app; _start(app, 8303, name)

        elif name == "web-search":
            from templates.general.web_search_server import app; _start(app, 8304, name)

        elif name == "database":
            if not _ensure_packages("sqlalchemy"):
                return False
            from templates.general.database_server import app; _start(app, 8305, name)

        elif name == "notion":
            from templates.general.notion_server import app; _start(app, 8307, name)

        elif name == "asana":
            from templates.general.asana_server import app; _start(app, 8308, name)

        elif name == "google-sheets":
            if not _ensure_packages("gspread", "google-auth"):
                return False
            from templates.general.google_sheets_server import app; _start(app, 8309, name)

        elif name == "figma":
            from templates.general.figma_server import app; _start(app, 8310, name)

        else:
            return False

        return True

    except Exception as e:
        log.warning(f"[{name}] failed to start: {e}")
        return False


# ── Start all servers based on .env ──────────────────────────────────────────
def start_all():
    """Start all servers whose credentials are present in .env"""
    started = []

    def try_start(name):
        if start_server(name):
            started.append(name)

    # QA
    if os.getenv("JIRA_URL") and os.getenv("JIRA_TOKEN") and os.getenv("JIRA_EMAIL"):
        try_start("jira")
    if os.getenv("TESTRAIL_URL") and os.getenv("TESTRAIL_KEY") and os.getenv("TESTRAIL_USER"):
        try_start("testrail")
    if os.getenv("XRAY_CLIENT_ID") and os.getenv("XRAY_CLIENT_SECRET"):
        try_start("xray")
    if os.getenv("PLAYWRIGHT_PROJECT_PATH"):
        try_start("playwright")
    if os.getenv("ALLURE_RESULTS_DIR"):
        try_start("allure")
    try_start("pytest-runner")
    try_start("selenium")

    # Dev
    if os.getenv("GITHUB_TOKEN"):
        try_start("github")
    if os.getenv("GITLAB_TOKEN"):
        try_start("gitlab")
    if os.getenv("AZURE_TOKEN") and os.getenv("AZURE_ORG"):
        try_start("azure-devops")
    if os.getenv("CONFLUENCE_URL") and os.getenv("CONFLUENCE_TOKEN"):
        try_start("confluence")
    if os.getenv("LINEAR_API_KEY"):
        try_start("linear")
    try_start("git-local")
    try_start("code-runner")

    # General
    if os.getenv("SLACK_TOKEN"):
        try_start("slack")
    if os.getenv("NOTION_TOKEN"):
        try_start("notion")
    if os.getenv("ASANA_TOKEN"):
        try_start("asana")
    if os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"):
        try_start("google-sheets")
    if os.getenv("FIGMA_TOKEN"):
        try_start("figma")
    if os.getenv("DATABASE_URL"):
        try_start("database")
    try_start("filesystem")
    try_start("rest-api")
    try_start("web-search")

    print(f"\n[server_manager] Started {len(started)} servers: {', '.join(started) if started else 'none'}")
    return started
