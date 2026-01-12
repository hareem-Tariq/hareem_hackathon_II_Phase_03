"""
MCP Client for OpenAI Agent Integration.
Provides utilities to fetch MCP tools and execute them within the agent.
"""
from typing import List, Dict, Any
from app.mcp.mcp_server import mcp_server
from sqlmodel import Session


async def get_mcp_tools_from_server() -> List[Dict[str, Any]]:
    """
    Get MCP tools from the official MCP server.
    Converts MCP Tool format to OpenAI function calling format.
    
    Returns:
        List of tool definitions in OpenAI function calling format.
    """
    from app.mcp.mcp_server import handle_list_tools
    
    # Get tools from MCP server handler
    tools = await handle_list_tools()
    
    # Convert to OpenAI format
    openai_tools = []
    for tool in tools:
        openai_tool = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        }
        openai_tools.append(openai_tool)
    
    return openai_tools


async def execute_mcp_tool(
    session: Session,
    tool_name: str,
    arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute an MCP tool through the official MCP server.
    
    Args:
        session: Database session (injected)
        tool_name: Name of the tool to execute
        arguments: Tool arguments (must include user_id)
        
    Returns:
        Tool execution result as dictionary
    """
    import json
    from app.mcp.mcp_server import handle_call_tool
    
    # Call the tool through MCP server handler
    result_contents = await handle_call_tool(tool_name, arguments)
    
    # Extract result from TextContent
    if result_contents:
        result_text = result_contents[0].text
        return json.loads(result_text)
    
    return {"error": "No result returned from tool"}


# Legacy compatibility: Keep existing function names
def get_mcp_tools() -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for get_mcp_tools_from_server.
    Used by legacy code that expects synchronous tools.
    
    Note: This creates a new event loop to run the async function.
    In async contexts, use get_mcp_tools_from_server() directly.
    """
    import asyncio
    
    # Allow nested event loops (needed when already in async context)
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass  # nest_asyncio might not be installed, that's ok
    except Exception:
        pass  # nest_asyncio might fail to apply, that's ok
    
    # Try to get existing loop, or create new one
    try:
        loop = asyncio.get_running_loop()
        # If we're in an async context, just create the task
        # This won't work perfectly but allows compatibility
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, get_mcp_tools_from_server())
            return future.result()
    except RuntimeError:
        # No loop running, create new one
        return asyncio.run(get_mcp_tools_from_server())


def get_tool_function(tool_name: str):
    """
    Get a tool function by name.
    
    This returns a wrapper that executes the tool through the MCP server.
    Maintains compatibility with existing agent code.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Async function that executes the tool
    """
    async def tool_wrapper(session: Session, **kwargs):
        """Wrapper function that calls MCP tool."""
        return await execute_mcp_tool(session, tool_name, kwargs)
    
    return tool_wrapper
