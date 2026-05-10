from pydantic import BaseModel, Field
from typing import Any, Optional


class ToolCallRequest(BaseModel):
    server: str = Field(..., description="Server name as registered in registry.json")
    tool: str = Field(..., description="Tool name to call")
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolCallResponse(BaseModel):
    success: bool
    result: Any = None
    server: str
    tool: str
    error: Optional[str] = None


class ServerInfo(BaseModel):
    name: str
    description: str = ""
    url: str
    transport: str = "http"
    tools: list[str] = Field(default_factory=list)
    trusted: bool = True
    added_by: Optional[str] = None
    added_at: Optional[str] = None


class GatewayStatus(BaseModel):
    status: str
    version: str
    servers_registered: int
    servers_healthy: int
