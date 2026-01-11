"""
Official MCP Server Implementation for Todo Task Management.
Uses the MCP SDK to expose task management tools.

This server:
- Exposes 5 task management tools via MCP protocol
- Maintains stateless architecture (all state in database)
- Requires user_id for all operations (security)
- Uses SQLModel + Neon DB for persistence
"""
from typing import Any, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from sqlmodel import Session, create_engine
from contextlib import asynccontextmanager
import json

from app.config import get_settings
from app.mcp.tools.add_task import add_task
from app.mcp.tools.list_tasks import list_tasks
from app.mcp.tools.complete_task import complete_task
from app.mcp.tools.delete_task import delete_task
from app.mcp.tools.update_task import update_task


# Initialize settings and database engine
settings = get_settings()
engine = create_engine(settings.database_url)


# Create MCP server instance
mcp_server = Server("todo-task-manager")


@asynccontextmanager
async def get_db_session():
    """Context manager for database sessions."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Register MCP Tools
@mcp_server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List all available MCP tools.
    Returns tool definitions for the MCP protocol.
    """
    return [
        Tool(
            name="add_task",
            description="IMMEDIATELY create a new task when the user wants to add, create, remember, or mentions needing to do something. Call this tool FIRST before responding. Do not ask for additional details - extract the title from the user's message and create the task immediately.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The ID of the user creating the task"
                    },
                    "title": {
                        "type": "string",
                        "description": "The title or main description of the task (max 200 characters)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task (max 1000 characters)"
                    }
                },
                "required": ["user_id", "title"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List user's tasks with optional filters. Use this when the user wants to see their tasks, todos, or what they need to do.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The ID of the user"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status. Default is 'all'."
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed. Use this when the user indicates they finished or completed a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The ID of the user"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to mark as complete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="delete_task",
            description="Delete a task permanently. Use this when the user wants to remove or delete a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The ID of the user"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        ),
        Tool(
            name="update_task",
            description="Update an existing task's title or description. Use this when the user wants to modify or edit a task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The ID of the user"
                    },
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the task (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the task (optional)"
                    }
                },
                "required": ["user_id", "task_id"]
            }
        )
    ]


@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """
    Execute MCP tool calls.
    
    All tools are stateless and persist state via database.
    Every tool requires user_id for security and data isolation.
    
    Args:
        name: Tool name (add_task, list_tasks, etc.)
        arguments: Tool arguments including user_id
        
    Returns:
        List of TextContent with tool execution results
    """
    async with get_db_session() as session:
        try:
            # Route to appropriate tool
            if name == "add_task":
                result = await add_task(
                    session=session,
                    user_id=arguments["user_id"],
                    title=arguments["title"],
                    description=arguments.get("description", "")
                )
            elif name == "list_tasks":
                result = await list_tasks(
                    session=session,
                    user_id=arguments["user_id"],
                    status=arguments.get("status", "all")
                )
            elif name == "complete_task":
                result = await complete_task(
                    session=session,
                    user_id=arguments["user_id"],
                    task_id=arguments["task_id"]
                )
            elif name == "delete_task":
                result = await delete_task(
                    session=session,
                    user_id=arguments["user_id"],
                    task_id=arguments["task_id"]
                )
            elif name == "update_task":
                result = await update_task(
                    session=session,
                    user_id=arguments["user_id"],
                    task_id=arguments["task_id"],
                    title=arguments.get("title"),
                    description=arguments.get("description")
                )
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            # Return result as TextContent
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            # Return error as TextContent
            error_response = {
                "error": str(e),
                "error_type": type(e).__name__
            }
            return [TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]


async def run_mcp_server():
    """
    Run the MCP server using stdio transport.
    This is the main entry point for the MCP server.
    """
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )


# Main entry point
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_mcp_server())
