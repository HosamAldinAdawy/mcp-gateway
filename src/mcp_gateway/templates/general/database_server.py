"""
MCP Gateway Template — Database Server
Run SQL queries on PostgreSQL, MySQL, or SQLite.

Setup:
  pip install fastapi uvicorn
  For PostgreSQL: pip install asyncpg
  For MySQL:      pip install aiomysql
  For SQLite:     built-in

  export DB_TYPE=postgresql  # or mysql or sqlite
  export DB_HOST=localhost
  export DB_PORT=5432
  export DB_NAME=mydb
  export DB_USER=myuser
  export DB_PASSWORD=mypassword
  python templates/general/database_server.py
"""
import os
import json
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Database MCP Server")

DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "gateway.db")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


async def get_connection():
    if DB_TYPE == "sqlite":
        import sqlite3
        return sqlite3.connect(DB_NAME)
    elif DB_TYPE == "postgresql":
        import asyncpg
        return await asyncpg.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    elif DB_TYPE == "mysql":
        import aiomysql
        return await aiomysql.connect(host=DB_HOST, port=DB_PORT, db=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    else:
        raise ValueError(f"Unsupported DB_TYPE: {DB_TYPE}")


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "database", "type": DB_TYPE}


@app.post("/call")
async def call(req: CallRequest):
    try:
        tools = {
            "query": do_query,
            "insert": do_insert,
            "update": do_update,
            "delete": do_delete,
            "list_tables": do_list_tables,
            "describe_table": do_describe_table,
        }
        if req.tool not in tools:
            return {"error": f"Unknown tool: {req.tool}"}
        return await tools[req.tool](**req.arguments)
    except Exception as e:
        return {"error": str(e)}


async def do_query(sql: str, params: list = []):
    # Safety check — read only
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT") and not sql_upper.startswith("SHOW") and not sql_upper.startswith("DESCRIBE"):
        return {"error": "Only SELECT queries are allowed via the query tool. Use insert/update/delete tools."}

    if DB_TYPE == "sqlite":
        import sqlite3
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return {"result": rows[:100]}
    else:
        conn = await get_connection()
        rows = await conn.fetch(sql, *params)
        await conn.close()
        return {"result": [dict(r) for r in rows[:100]]}


async def do_insert(table: str, data: dict):
    cols = ", ".join(data.keys())
    vals = ", ".join([f"'{v}'" for v in data.values()])
    sql = f"INSERT INTO {table} ({cols}) VALUES ({vals})"
    if DB_TYPE == "sqlite":
        import sqlite3
        conn = sqlite3.connect(DB_NAME)
        conn.execute(sql)
        conn.commit()
        conn.close()
    else:
        conn = await get_connection()
        await conn.execute(sql)
        await conn.close()
    return {"result": f"Inserted into {table}"}


async def do_update(table: str, data: dict, where: str):
    sets = ", ".join([f"{k}='{v}'" for k, v in data.items()])
    sql = f"UPDATE {table} SET {sets} WHERE {where}"
    if DB_TYPE == "sqlite":
        import sqlite3
        conn = sqlite3.connect(DB_NAME)
        conn.execute(sql)
        conn.commit()
        conn.close()
    else:
        conn = await get_connection()
        await conn.execute(sql)
        await conn.close()
    return {"result": f"Updated {table} where {where}"}


async def do_delete(table: str, where: str):
    sql = f"DELETE FROM {table} WHERE {where}"
    if DB_TYPE == "sqlite":
        import sqlite3
        conn = sqlite3.connect(DB_NAME)
        conn.execute(sql)
        conn.commit()
        conn.close()
    else:
        conn = await get_connection()
        await conn.execute(sql)
        await conn.close()
    return {"result": f"Deleted from {table} where {where}"}


async def do_list_tables():
    if DB_TYPE == "sqlite":
        import sqlite3
        conn = sqlite3.connect(DB_NAME)
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        conn.close()
    elif DB_TYPE == "postgresql":
        conn = await get_connection()
        rows = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        tables = [r["tablename"] for r in rows]
        await conn.close()
    else:
        tables = []
    return {"result": tables}


async def do_describe_table(table: str):
    if DB_TYPE == "sqlite":
        import sqlite3
        conn = sqlite3.connect(DB_NAME)
        cur = conn.execute(f"PRAGMA table_info({table})")
        cols = [{"name": r[1], "type": r[2], "nullable": not r[3]} for r in cur.fetchall()]
        conn.close()
    elif DB_TYPE == "postgresql":
        conn = await get_connection()
        rows = await conn.fetch(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name='{table}'")
        cols = [dict(r) for r in rows]
        await conn.close()
    else:
        cols = []
    return {"result": cols}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("DATABASE_PORT", "8302")))
