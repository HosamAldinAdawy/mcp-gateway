import os
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()

from gateway.models import GatewayStatus
from gateway.router import router
from gateway.transport.sse import mcp_router
from registry.registry import get_all_servers
from registry.validator import count_healthy

VERSION = "1.0.0"
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    servers = get_all_servers()
    print(f"\n MCP Gateway v{VERSION}")
    print(f" Servers registered: {len(servers)}")
    for s in servers:
        print(f"   - {s.name} ({s.url})")
    print(f"\n Web UI:    http://localhost:8000")
    print(f" API docs:  http://localhost:8000/docs")
    print(f" MCP (SSE): http://localhost:8000/mcp\n")
    yield


app = FastAPI(
    title="MCP Gateway",
    description="Secure remote MCP gateway — auth, audit, registry, SSE transport.",
    version=VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API
app.include_router(router, prefix="/v1")

# Remote MCP (SSE)
app.include_router(mcp_router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": VERSION}


@app.get("/status", response_model=GatewayStatus)
async def gateway_status():
    servers = get_all_servers()
    healthy = await count_healthy()
    return GatewayStatus(
        status="ok", version=VERSION,
        servers_registered=len(servers),
        servers_healthy=healthy,
    )


# Serve React UI — must be last
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_ui(full_path: str = ""):
        # Don't intercept API routes
        if full_path.startswith(("v1/", "health", "status", "docs", "openapi", "mcp")):
            return None
        index = STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(index)
        return {"message": "UI not built yet. Run: cd ui && npm install && npm run build"}
