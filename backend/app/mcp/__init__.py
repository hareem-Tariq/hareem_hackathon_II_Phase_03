"""
MCP package initialization.
Exports official MCP SDK integration and legacy compatibility functions.
"""
from app.mcp.client import (
    get_mcp_tools,
    get_tool_function,
    get_mcp_tools_from_server,
    execute_mcp_tool
)
from app.mcp.mcp_server import mcp_server

__all__ = [
    "get_mcp_tools",
    "get_tool_function",
    "get_mcp_tools_from_server",
    "execute_mcp_tool",
    "mcp_server"
]
