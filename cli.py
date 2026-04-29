#!/usr/bin/env python3
"""
MCP Gateway CLI — manage your local server registry.

Usage:
  python cli.py list
  python cli.py add --name my-server --url http://localhost:8002 --tools tool1,tool2 --desc "My server"
  python cli.py remove --name my-server
"""
import argparse
import json
import sys

sys.path.insert(0, ".")
from registry.registry import add_server, remove_server, get_all_servers


def cmd_list(args):
    servers = get_all_servers()
    if not servers:
        print("No servers registered.")
        return
    print(f"\n{'NAME':<20} {'URL':<30} {'TOOLS':<30} TRUSTED")
    print("-" * 85)
    for s in servers:
        tools = ", ".join(s.tools)
        print(f"{s.name:<20} {s.url:<30} {tools:<30} {'yes' if s.trusted else 'no'}")
    print()


def cmd_add(args):
    tools = [t.strip() for t in args.tools.split(",")]
    server = add_server(
        name=args.name,
        description=args.desc,
        url=args.url,
        transport=args.transport,
        tools=tools,
    )
    print(f"Added server '{server.name}' to registry.")


def cmd_remove(args):
    ok = remove_server(args.name)
    if ok:
        print(f"Removed server '{args.name}' from registry.")
    else:
        print(f"Server '{args.name}' not found.")


def main():
    parser = argparse.ArgumentParser(description="MCP Gateway CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all registered servers")

    add_p = sub.add_parser("add", help="Add a server to the registry")
    add_p.add_argument("--name", required=True)
    add_p.add_argument("--url", required=True)
    add_p.add_argument("--tools", required=True, help="Comma-separated tool names")
    add_p.add_argument("--desc", default="")
    add_p.add_argument("--transport", default="http")

    rem_p = sub.add_parser("remove", help="Remove a server from the registry")
    rem_p.add_argument("--name", required=True)

    args = parser.parse_args()
    if args.command == "list":
        cmd_list(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "remove":
        cmd_remove(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
