#!/usr/bin/env python3
"""
MCP Gateway — Interactive Setup Wizard
Run: python setup/wizard.py
"""
import json
import os
import sys
import secrets
from pathlib import Path

ROOT = Path(__file__).parent.parent

BANNER = """
╔══════════════════════════════════════════╗
║         MCP Gateway Setup Wizard         ║
║   Secure local gateway for MCP servers   ║
╚══════════════════════════════════════════╝
"""

TEMPLATES = {
    # QA Tools
    "jira": {
        "category": "qa",
        "name": "jira",
        "description": "Jira issue tracking — create bugs, search issues, update status",
        "url": "http://localhost:8101",
        "tools": ["create_issue", "search_issues", "update_issue", "get_issue", "add_comment"],
    },
    "testrail": {
        "category": "qa",
        "name": "testrail",
        "description": "TestRail test management — manage test cases, runs, and results",
        "url": "http://localhost:8102",
        "tools": ["get_test_cases", "create_test_case", "add_result", "get_run", "create_run"],
    },
    "xray": {
        "category": "qa",
        "name": "xray",
        "description": "Xray for Jira — BDD test management and execution tracking",
        "url": "http://localhost:8103",
        "tools": ["create_test", "update_execution", "get_test_plan", "import_results"],
    },
    "zephyr": {
        "category": "qa",
        "name": "zephyr",
        "description": "Zephyr Scale — test cycles and execution tracking inside Jira",
        "url": "http://localhost:8104",
        "tools": ["create_cycle", "add_execution", "get_results", "update_status"],
    },
    "pytest": {
        "category": "qa",
        "name": "pytest-runner",
        "description": "Pytest runner — execute tests and parse results",
        "url": "http://localhost:8105",
        "tools": ["run_tests", "get_results", "run_suite", "get_coverage"],
    },
    "allure": {
        "category": "qa",
        "name": "allure-reporter",
        "description": "Allure — generate and read test reports",
        "url": "http://localhost:8106",
        "tools": ["generate_report", "get_summary", "get_failures", "get_history"],
    },
    "bdd": {
        "category": "qa",
        "name": "bdd-generator",
        "description": "BDD Generator — generate Gherkin scenarios from requirements",
        "url": "http://localhost:8107",
        "tools": ["generate_scenarios", "validate_gherkin", "export_feature"],
    },
    # Dev Tools
    "github": {
        "category": "dev",
        "name": "github",
        "description": "GitHub — manage repos, PRs, issues, and branches",
        "url": "http://localhost:8201",
        "tools": ["create_issue", "list_prs", "get_pr", "merge_pr", "create_branch", "get_commits"],
    },
    "git": {
        "category": "dev",
        "name": "git-local",
        "description": "Local Git — status, diff, commit, log",
        "url": "http://localhost:8202",
        "tools": ["status", "diff", "commit", "log", "branch", "checkout"],
    },
    "azure_devops": {
        "category": "dev",
        "name": "azure-devops",
        "description": "Azure DevOps — work items, pipelines, and test plans",
        "url": "http://localhost:8203",
        "tools": ["create_work_item", "get_pipeline", "run_pipeline", "get_test_plan"],
    },
    "code_runner": {
        "category": "dev",
        "name": "code-runner",
        "description": "Code Runner — execute Python or JS in a sandbox",
        "url": "http://localhost:8204",
        "tools": ["run_python", "run_javascript", "run_shell"],
    },
    # General Tools
    "filesystem": {
        "category": "general",
        "name": "filesystem",
        "description": "File System — read, write, search files",
        "url": "http://localhost:8301",
        "tools": ["read_file", "write_file", "search_files", "list_dir", "delete_file"],
    },
    "database": {
        "category": "general",
        "name": "database",
        "description": "Database — run SQL queries on any DB",
        "url": "http://localhost:8302",
        "tools": ["query", "insert", "update", "delete", "list_tables", "describe_table"],
    },
    "rest_api": {
        "category": "general",
        "name": "rest-api-caller",
        "description": "REST API Caller — call any external HTTP API",
        "url": "http://localhost:8303",
        "tools": ["get", "post", "put", "patch", "delete"],
    },
    "browser": {
        "category": "general",
        "name": "browser",
        "description": "Browser / Web Scraper — navigate, scrape, screenshot",
        "url": "http://localhost:8304",
        "tools": ["navigate", "scrape", "screenshot", "fill_form", "click"],
    },
    "slack": {
        "category": "general",
        "name": "slack",
        "description": "Slack — send messages and notifications",
        "url": "http://localhost:8305",
        "tools": ["send_message", "list_channels", "get_messages", "create_channel"],
    },
    "web_search": {
        "category": "general",
        "name": "web-search",
        "description": "Web Search — search the web in real time",
        "url": "http://localhost:8306",
        "tools": ["search", "fetch_page", "summarize_url"],
    },
}

LLM_CONFIGS = {
    "1": "Claude Desktop",
    "2": "Cursor",
    "3": "VS Code",
    "4": "Python SDK",
    "5": "Custom / Other",
}


def print_color(text, color="white"):
    colors = {
        "green": "\033[92m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m",
        "bold": "\033[1m",
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")


def ask(prompt, default=None):
    if default:
        val = input(f"{prompt} [{default}]: ").strip()
        return val if val else default
    return input(f"{prompt}: ").strip()


def ask_choice(prompt, options: dict):
    print_color(f"\n{prompt}", "cyan")
    for k, v in options.items():
        print(f"  {k}. {v}")
    while True:
        choice = input("\nاختار رقم: ").strip()
        if choice in options:
            return choice
        print_color("اختار رقم صح من القايمة.", "red")


def ask_multiselect(prompt, options: dict):
    print_color(f"\n{prompt}", "cyan")
    print_color("(اكتب الأرقام مفصولة بفاصلة — مثلاً: 1,3,5)", "yellow")
    print_color("(اكتب 0 لتختار كل حاجة)", "yellow")
    for k, v in options.items():
        print(f"  {k}. {v}")
    while True:
        raw = input("\nاختار: ").strip()
        if raw == "0":
            return list(options.keys())
        selected = [x.strip() for x in raw.split(",")]
        if all(s in options for s in selected):
            return selected
        print_color("اختار أرقام صح من القايمة.", "red")


def setup_env(api_key):
    env_path = ROOT / ".env"
    example_path = ROOT / ".env.example"
    if not env_path.exists() and example_path.exists():
        content = example_path.read_text()
        content = content.replace("your-secret-key-here", api_key)
        env_path.write_text(content)
        print_color("تم إنشاء ملف .env", "green")
    else:
        content = env_path.read_text()
        if "your-secret-key-here" in content:
            content = content.replace("your-secret-key-here", api_key)
            env_path.write_text(content)
            print_color("تم تحديث ملف .env بالـ API key", "green")


def add_to_registry(servers_to_add):
    registry_path = ROOT / "registry" / "registry.json"
    with open(registry_path) as f:
        data = json.load(f)

    existing = {s["name"] for s in data["servers"]}
    added = []

    for key in servers_to_add:
        t = TEMPLATES[key]
        if t["name"] not in existing:
            data["servers"].append({
                "name": t["name"],
                "description": t["description"],
                "url": t["url"],
                "transport": "http",
                "tools": t["tools"],
                "trusted": True,
                "added_by": "wizard",
                "added_at": "2025-01-01T00:00:00Z",
            })
            added.append(t["name"])

    with open(registry_path, "w") as f:
        json.dump(data, f, indent=2)

    return added


def generate_llm_config(llm_choice, api_key, port=8000):
    gateway_url = f"http://localhost:{port}"

    if llm_choice == "1":  # Claude Desktop
        config = {
            "mcpServers": {
                "mcp-gateway": {
                    "command": "curl",
                    "args": ["-s", "-H", f"X-API-Key: {api_key}", f"{gateway_url}/v1/servers"],
                    "env": {"MCP_GATEWAY_URL": gateway_url, "MCP_API_KEY": api_key},
                }
            }
        }
        path = ROOT / "docs" / "claude-desktop-config.json"
        path.write_text(json.dumps(config, indent=2))
        print_color(f"\nClaude Desktop config saved: docs/claude-desktop-config.json", "green")
        print_color("انسخ محتواه لـ: ~/Library/Application Support/Claude/claude_desktop_config.json", "yellow")

    elif llm_choice == "2":  # Cursor
        config = {"mcp": {"servers": {"mcp-gateway": {"url": f"{gateway_url}/v1", "headers": {"X-API-Key": api_key}}}}}
        path = ROOT / "docs" / "cursor-mcp-config.json"
        path.write_text(json.dumps(config, indent=2))
        print_color(f"\nCursor config saved: docs/cursor-mcp-config.json", "green")
        print_color("انسخ محتواه لـ: ~/.cursor/mcp.json", "yellow")

    elif llm_choice == "4":  # Python SDK
        code = f'''import httpx

GATEWAY_URL = "{gateway_url}/v1"
API_KEY = "{api_key}"

def call_tool(server: str, tool: str, arguments: dict):
    response = httpx.post(
        f"{{GATEWAY_URL}}/call",
        headers={{"X-API-Key": API_KEY}},
        json={{"server": server, "tool": tool, "arguments": arguments}},
    )
    return response.json()

# مثال
result = call_tool("echo-server", "echo", {{"message": "Hello!"}})
print(result)
'''
        path = ROOT / "docs" / "python-sdk-example.py"
        path.write_text(code)
        print_color(f"\nPython example saved: docs/python-sdk-example.py", "green")


def mode_templates():
    print_color("\n── اختار الـ Templates ──", "bold")

    categories = {
        "1": "QA Tools (Jira, TestRail, Xray, Pytest...)",
        "2": "Dev Tools (GitHub, Git, Azure DevOps...)",
        "3": "General Tools (Files, Database, Browser...)",
        "4": "كل الـ templates",
    }

    cat_choice = ask_multiselect("اختار الفئات اللي محتاجها:", categories)

    selected_keys = []

    if "4" in cat_choice:
        selected_keys = list(TEMPLATES.keys())
    else:
        cat_map = {"1": "qa", "2": "dev", "3": "general"}
        selected_cats = [cat_map[c] for c in cat_choice if c in cat_map]

        filtered = {
            k: f"{v['description']}"
            for k, v in TEMPLATES.items()
            if v["category"] in selected_cats
        }

        template_choices = ask_multiselect(
            "اختار الـ templates اللي عايزها:", filtered
        )
        selected_keys = template_choices

    return selected_keys


def mode_manual():
    print_color("\n── إنشاء Server من الصفر ──", "bold")
    name = ask("اسم الـ server (مثلاً: my-tool)")
    description = ask("وصف قصير للـ server")
    url = ask("الـ URL", "http://localhost:8001")
    tools_raw = ask("أسماء الـ tools مفصولة بفاصلة (مثلاً: tool1,tool2)")
    tools = [t.strip() for t in tools_raw.split(",") if t.strip()]

    custom = {
        "custom": {
            "category": "custom",
            "name": name,
            "description": description,
            "url": url,
            "tools": tools,
        }
    }
    TEMPLATES["custom"] = custom["custom"]
    return ["custom"]


def mode_import():
    print_color("\n── استيراد Config موجود ──", "bold")
    path = ask("مسار ملف الـ registry.json القديم")
    try:
        with open(path) as f:
            data = json.load(f)
        registry_path = ROOT / "registry" / "registry.json"
        with open(registry_path) as f:
            current = json.load(f)
        existing = {s["name"] for s in current["servers"]}
        added = []
        for s in data.get("servers", []):
            if s["name"] not in existing:
                current["servers"].append(s)
                added.append(s["name"])
        with open(registry_path, "w") as f:
            json.dump(current, f, indent=2)
        print_color(f"\nتم استيراد {len(added)} servers.", "green")
        return []
    except Exception as e:
        print_color(f"خطأ في الاستيراد: {e}", "red")
        return []


def main():
    print_color(BANNER, "cyan")

    # Step 1 — Mode
    mode = ask_choice(
        "كيف تريد تبدأ؟",
        {
            "1": "اختار من templates جاهزة  ← أسرع",
            "2": "أنشئ server من الصفر      ← تحكم كامل",
            "3": "استورد config موجود        ← لو عندك setup قديم",
        },
    )

    # Step 2 — Collect servers
    if mode == "1":
        selected_keys = mode_templates()
    elif mode == "2":
        selected_keys = mode_manual()
    else:
        selected_keys = mode_import()

    # Step 3 — LLM choice
    llm_choice = ask_choice(
        "هتستخدم الـ gateway مع إيه؟",
        LLM_CONFIGS,
    )

    # Step 4 — API Key
    print_color("\n── إعداد الـ API Key ──", "bold")
    generated_key = secrets.token_urlsafe(32)
    print_color(f"API key مقترح: {generated_key}", "yellow")
    api_key = ask("اضغط Enter لاستخدامه أو اكتب key خاص بيك", generated_key)

    # Step 5 — Apply
    print_color("\n── جاري الإعداد... ──", "bold")

    setup_env(api_key)

    if selected_keys:
        added = add_to_registry(selected_keys)
        for name in added:
            print_color(f"تم إضافة: {name}", "green")

    generate_llm_config(llm_choice, api_key)

    # Step 6 — Done
    print_color("\n" + "═" * 44, "cyan")
    print_color("تم الإعداد بنجاح!", "green")
    print_color("═" * 44, "cyan")
    print_color("\nلتشغيل الـ gateway:", "white")
    print_color("  make run", "yellow")
    print_color("\nلاختبار كل حاجة:", "white")
    print_color("  make test", "yellow")
    print_color("\nلمتابعة الـ audit logs:", "white")
    print_color("  make logs", "yellow")
    print_color("\nAPI Key بتاعك:", "white")
    print_color(f"  {api_key}", "yellow")
    print_color("\nاحتفظ بالـ API key في مكان آمن!\n", "red")


if __name__ == "__main__":
    main()
