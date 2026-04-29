"""
MCP Gateway Template — Google Sheets Server
Read and write Google Sheets data.

Setup:
  pip install fastapi uvicorn httpx google-auth google-auth-oauthlib google-auth-httplib2 gspread
  export GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
  python templates/general/google_sheets_server.py
"""
import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

app = FastAPI(title="Google Sheets MCP Server")

SA_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")


def get_client():
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = ["https://spreadsheets.google.com/feeds",
              "https://www.googleapis.com/auth/drive"]
    if SA_JSON and os.path.exists(SA_JSON):
        creds = Credentials.from_service_account_file(SA_JSON, scopes=scopes)
    else:
        info = json.loads(SA_JSON)
        creds = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(creds)


class CallRequest(BaseModel):
    tool: str
    arguments: dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "server": "google_sheets"}


@app.post("/call")
async def call(req: CallRequest):
    try:
        if req.tool == "read_sheet":
            return await read_sheet(**req.arguments)
        elif req.tool == "write_row":
            return await write_row(**req.arguments)
        elif req.tool == "update_cell":
            return await update_cell(**req.arguments)
        elif req.tool == "append_rows":
            return await append_rows(**req.arguments)
        elif req.tool == "get_sheet_info":
            return await get_sheet_info(**req.arguments)
        elif req.tool == "clear_range":
            return await clear_range(**req.arguments)
        else:
            raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def read_sheet(spreadsheet_id: str, sheet_name: str = "Sheet1",
                     range: str = None):
    gc = get_client()
    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet(sheet_name)
    if range:
        return {"values": ws.get(range)}
    return {"values": ws.get_all_values(), "total_rows": ws.row_count}


async def write_row(spreadsheet_id: str, values: list, sheet_name: str = "Sheet1"):
    gc = get_client()
    ws = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
    ws.append_row(values)
    return {"success": True, "appended": values}


async def update_cell(spreadsheet_id: str, cell: str, value: str,
                      sheet_name: str = "Sheet1"):
    gc = get_client()
    ws = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
    ws.update_acell(cell, value)
    return {"success": True, "cell": cell, "value": value}


async def append_rows(spreadsheet_id: str, rows: list, sheet_name: str = "Sheet1"):
    gc = get_client()
    ws = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
    ws.append_rows(rows)
    return {"success": True, "rows_added": len(rows)}


async def get_sheet_info(spreadsheet_id: str):
    gc = get_client()
    sh = gc.open_by_key(spreadsheet_id)
    return {
        "title": sh.title,
        "sheets": [{"name": ws.title, "rows": ws.row_count,
                    "cols": ws.col_count} for ws in sh.worksheets()],
    }


async def clear_range(spreadsheet_id: str, range: str, sheet_name: str = "Sheet1"):
    gc = get_client()
    ws = gc.open_by_key(spreadsheet_id).worksheet(sheet_name)
    ws.batch_clear([range])
    return {"success": True, "cleared": range}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8309)
