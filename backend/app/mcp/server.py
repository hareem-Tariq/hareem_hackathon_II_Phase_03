"""
MCP Server - Tool registration and management.
Provides stateless MCP tools for task management operations.
"""
from typing import List, Dict, Any, Callable
from app.mcp.tools.add_task import add_task
from app.mcp.tools.list_tasks import list_tasks
from app.mcp.tools.update_task import update_task
from app.mcp.tools.delete_task import delete_task
from app.mcp.tools.complete_task import complete_task


def get_mcp_tools() -> List[Dict[str, Any]]:
    """
    Get all MCP tool definitions for OpenAI function calling.
    
    Returns:
        List of tool definitions in OpenAI function calling format.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something.",
                "parameters": {
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
                            "description": "Optional detailed description of the task (max 1000 characters)",
                            "default": ""
                        }
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List user's tasks with optional filters. Use this when the user wants to see their tasks, todos, or what they need to do.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by status. Default is 'all'.",
                            "default": "all"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Update an existing task's title or description. Use this when the user wants to modify or edit a task.",
                "parameters": {
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
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as completed or uncompleted. Use this when the user says they finished, completed, or done with a task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to complete"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "True to mark as completed, False to mark as pending",
                            "default": True
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task permanently. Use this when the user wants to remove or delete a task.",
                "parameters": {
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
            }
        }
    ]


def get_tool_function(tool_name: str) -> Callable:
    """
    Get the actual function implementation for a tool.
    
    Args:
        tool_name: Name of the tool function
        
    Returns:
        The callable function
    """
    tools = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "update_task": update_task,
        "complete_task": complete_task,
        "delete_task": delete_task
    }
    return tools.get(tool_name)
