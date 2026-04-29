#!/usr/bin/env python3
"""
mcp-gateway CLI entry point.

Usage after pip install:
  mcp-gateway start          ← شغّل الـ gateway
  mcp-gateway setup          ← setup wizard
  mcp-gateway init           ← create .env in current dir
  mcp-gateway list           ← list registered servers
  mcp-gateway add ...        ← add server
  mcp-gateway remove ...     ← remove server
  mcp-gateway version        ← show version
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).parent
VERSION = "1.0.0"


def cmd_start(args):
    """Start the MCP Gateway server."""
    env_file = Path(".env")
    if not env_file.exists():
        example = PACKAGE_DIR / ".env.example"
        if example.exists():
            shutil.copy(example, env_file)
            print("✅ Created .env from template — edit it to set your API keys.")
        else:
            env_file.write_text("MCP_API_KEYS=change-me-before-use\n")
            print("⚠️  Created minimal .env — set MCP_API_KEYS before use!")

    port = args.port or int(os.getenv("PORT", 8000))
    host = args.host or os.getenv("HOST", "0.0.0.0")
    reload = args.reload

    print(f"\n🚀 Starting MCP Gateway v{VERSION}")
    print(f"   http://{host}:{port}\n")

    import sys
    # Make sure current dir is on path so registry.json / .env are found
    sys.path.insert(0, str(PACKAGE_DIR))
    sys.path.insert(0, ".")

    try:
        import uvicorn
        uvicorn.run(
            "mcp_gateway.gateway.main:app",
            host=host,
            port=port,
            reload=reload,
        )
    except ImportError:
        print("❌ uvicorn not found. Run: pip install mcp-gateway")
        sys.exit(1)


def cmd_init(args):
    """Copy starter files (.env, registry.json) into the current working directory."""
    cwd = Path(".")

    # .env
    env_dest = cwd / ".env"
    if not env_dest.exists():
        src = PACKAGE_DIR / ".env.example"
        if src.exists():
            shutil.copy(src, env_dest)
            print(f"✅ Created .env — open it and set MCP_API_KEYS")
        else:
            env_dest.write_text(
                "MCP_API_KEYS=change-me-before-use\n"
                "HOST=0.0.0.0\n"
                "PORT=8000\n"
            )
            print(f"✅ Created minimal .env")
    else:
        print(f"⚠️  .env already exists, skipping")

    # registry.json
    reg_dest = cwd / "registry" / "registry.json"
    reg_dest.parent.mkdir(exist_ok=True)
    if not reg_dest.exists():
        src = PACKAGE_DIR / "registry" / "registry.json"
        if src.exists():
            shutil.copy(src, reg_dest)
            print(f"✅ Created registry/registry.json")
    else:
        print(f"⚠️  registry/registry.json already exists, skipping")

    # security/policy.json
    pol_dest = cwd / "security" / "policy.json"
    pol_dest.parent.mkdir(exist_ok=True)
    if not pol_dest.exists():
        src = PACKAGE_DIR / "security" / "policy.json"
        if src.exists():
            shutil.copy(src, pol_dest)
            print(f"✅ Created security/policy.json")

    print(f"\n✅ Init complete. Next:")
    print(f"   1. Edit .env  →  set MCP_API_KEYS")
    print(f"   2. mcp-gateway start")


def cmd_setup(args):
    """Run the interactive setup wizard."""
    wizard = PACKAGE_DIR / "setup" / "wizard.py"
    if not wizard.exists():
        print("❌ Setup wizard not found.")
        sys.exit(1)
    sys.path.insert(0, str(PACKAGE_DIR))
    sys.path.insert(0, ".")
    exec(wizard.read_text(), {"__name__": "__main__"})


def cmd_list(args):
    sys.path.insert(0, str(PACKAGE_DIR))
    sys.path.insert(0, ".")
    from mcp_gateway.registry.registry import get_all_servers
    servers = get_all_servers()
    if not servers:
        print("No servers registered.")
        return
    print(f"\n{'NAME':<20} {'URL':<35} {'TOOLS':<30} TRUSTED")
    print("-" * 90)
    for s in servers:
        tools = ", ".join(s.tools)
        print(f"{s.name:<20} {s.url:<35} {tools:<30} {'yes' if s.trusted else 'no'}")
    print()


def cmd_add(args):
    sys.path.insert(0, str(PACKAGE_DIR))
    sys.path.insert(0, ".")
    from mcp_gateway.registry.registry import add_server
    tools = [t.strip() for t in args.tools.split(",")]
    server = add_server(
        name=args.name,
        description=args.desc or "",
        url=args.url,
        transport=args.transport,
        tools=tools,
    )
    print(f"✅ Added server '{server.name}'")


def cmd_remove(args):
    sys.path.insert(0, str(PACKAGE_DIR))
    sys.path.insert(0, ".")
    from mcp_gateway.registry.registry import remove_server
    ok = remove_server(args.name)
    if ok:
        print(f"✅ Removed server '{args.name}'")
    else:
        print(f"❌ Server '{args.name}' not found")


def cmd_version(args):
    print(f"mcp-gateway {VERSION}")


def main():
    parser = argparse.ArgumentParser(
        prog="mcp-gateway",
        description="🔒 MCP Gateway — secure remote MCP with auth, audit & registry",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # start
    p_start = sub.add_parser("start", help="Start the gateway server")
    p_start.add_argument("--host", default=None, help="Host (default: 0.0.0.0)")
    p_start.add_argument("--port", type=int, default=None, help="Port (default: 8000)")
    p_start.add_argument("--reload", action="store_true", help="Auto-reload on code changes")

    # init
    sub.add_parser("init", help="Create starter .env + registry files in current dir")

    # setup
    sub.add_parser("setup", help="Run interactive setup wizard")

    # list
    sub.add_parser("list", help="List registered MCP servers")

    # add
    p_add = sub.add_parser("add", help="Add a server to the registry")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--url", required=True)
    p_add.add_argument("--tools", required=True, help="Comma-separated tool names")
    p_add.add_argument("--desc", default="")
    p_add.add_argument("--transport", default="http")

    # remove
    p_rem = sub.add_parser("remove", help="Remove a server from the registry")
    p_rem.add_argument("--name", required=True)

    # version
    sub.add_parser("version", help="Show version")

    args = parser.parse_args()

    dispatch = {
        "start": cmd_start,
        "init": cmd_init,
        "setup": cmd_setup,
        "list": cmd_list,
        "add": cmd_add,
        "remove": cmd_remove,
        "version": cmd_version,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()
        print("\nExamples:")
        print("  mcp-gateway init          # create .env in current dir")
        print("  mcp-gateway start         # start gateway on :8000")
        print("  mcp-gateway start --port 9000 --reload")
        print("  mcp-gateway list          # show registered servers")


if __name__ == "__main__":
    main()
