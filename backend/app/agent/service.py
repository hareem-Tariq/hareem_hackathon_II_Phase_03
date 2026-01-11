"""
OpenAI Agent Service - Manages AI agent for conversational task management.
Handles conversation state, tool calling, and response generation.

ARCHITECTURE NOTES:
- Stateless agent: No memory stored in RAM
- Conversation state: Loaded from database per request
- Agent creation: Fresh instance per request using environment API key
- MCP tools: Attached as callable functions per request
- Error handling: All errors converted to user-friendly messages
"""
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from openai import AsyncOpenAI, APIError, RateLimitError, APIConnectionError, AuthenticationError
from sqlmodel import Session, select

from app.config import get_settings
from app.models.conversation import Conversation
from app.models.message import Message
from app.agent.config import (
    get_agent_config,
    get_agent_system_prompt,
    build_agent_messages,
    get_context_window_size
)
from app.mcp.client import get_mcp_tools, execute_mcp_tool
from app.mcp.errors import DatabaseError, OpenAIAPIError


def load_message_history(
    session: Session,
    conversation_id: int,
    limit: Optional[int] = None
) -> List[Message]:
    """
    Load message history from database.
    
    Args:
        session: Database session
        conversation_id: ID of conversation
        limit: Maximum number of messages (defaults to MAX_CONTEXT_MESSAGES)
        
    Returns:
        List of messages, ordered from oldest to newest
    """
    if limit is None:
        limit = get_context_window_size()
    
    query = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    
    messages = session.exec(query).all()
    # Reverse to get chronological order (oldest first)
    return list(reversed(messages))


async def process_chat_message(
    session: Session,
    user_id: str,
    message: str,
    conversation_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Process a chat message using OpenAI Agents with MCP tools.
    Completely stateless - loads conversation from DB, processes, saves back.
    
    STATELESS DESIGN:
    - Creates fresh OpenAI client per request using environment API key
    - Loads conversation history from database
    - No agent memory stored in RAM
    - Context window: Last 50 messages only
    
    Args:
        session: Database session (injected dependency)
        user_id: The ID of the user
        message: User's message text
        conversation_id: Optional existing conversation ID
        
    Returns:
        Dictionary with conversation_id, response, and tool_calls
    """
    # Create fresh OpenAI client per request (stateless)
    # Uses API key from environment via get_agent_config()
    agent_config = get_agent_config()
    client = AsyncOpenAI(api_key=agent_config["api_key"])
    
    try:
        # Step 1: Get or create conversation
        if conversation_id:
            conversation = session.get(Conversation, conversation_id)
            if not conversation or conversation.user_id != user_id:
                raise ValueError(f"Conversation {conversation_id} not found or doesn't belong to user")
        else:
            conversation = Conversation(user_id=user_id)
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
    except Exception as e:
        raise DatabaseError() from e
    
    try:
        # Step 2: Store user message in database
        user_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="user",
            content=message
        )
        session.add(user_message)
        session.commit()
    except Exception as e:
        raise DatabaseError() from e
    
    try:
        # Step 3: Load last N messages from database (context window)
        history_messages = load_message_history(
            session=session,
            conversation_id=conversation.id,
            limit=get_context_window_size()
        )
    except Exception as e:
        raise DatabaseError() from e
    
    # Step 4: Build messages for OpenAI (system + history)
    # Includes system prompt with behavior rules
    # Convert Message objects to dictionaries
    history_dicts = [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages
    ]
    openai_messages = build_agent_messages(history_dicts)
    
    # Step 5: Get MCP tools (stateless - loaded per request)
    mcp_tools = get_mcp_tools()
    
    # Step 6: Call OpenAI with tools
    tool_calls_made = []
    
    try:
        # Initial completion with tools available
        response = await client.chat.completions.create(
            model=agent_config["model"],
            messages=openai_messages,
            tools=mcp_tools,
            temperature=agent_config["temperature"],
            max_tokens=agent_config["max_tokens"]
        )
    except AuthenticationError as e:
        # Invalid or missing API key - graceful fallback
        assistant_content = (
            "I'm currently unable to process AI responses because the OpenAI API key is not properly configured. "
            "However, the system is fully set up and ready! Your messages are being saved to the database. "
            "Once the API key is configured, I'll be able to help you manage your tasks with natural language."
        )
        
        # Store fallback message in database
        try:
            assistant_message = Message(
                conversation_id=conversation.id,
                user_id=user_id,
                role="assistant",
                content=assistant_content
            )
            session.add(assistant_message)
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)
            session.commit()
        except Exception as db_error:
            raise DatabaseError() from db_error
        
        return {
            "conversation_id": conversation.id,
            "response": assistant_content,
            "tool_calls": []
        }
    except RateLimitError as e:
        raise OpenAIAPIError(retry_after=60) from e
    except APIConnectionError as e:
        raise OpenAIAPIError(retry_after=30) from e
    except APIError as e:
        raise OpenAIAPIError(retry_after=15) from e
    
    message_response = response.choices[0].message
    
    # Step 7: Handle tool calls if any
    if message_response.tool_calls:
        # Append assistant's tool call message
        openai_messages.append(message_response)
        
        # Execute each tool call
        for tool_call in message_response.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # Add user_id to tool arguments (required by all tools)
            tool_args["user_id"] = user_id
            
            # Execute MCP tool
            tool_result = await execute_mcp_tool(session, tool_name, tool_args)
            
            # Record tool call
            tool_calls_made.append({
                "tool": tool_name,
                "arguments": tool_args,
                "result": tool_result
            })
            
            # Append tool result message
            openai_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })
        
        try:
            # Final completion with tool results
            final_response = await client.chat.completions.create(
                model=agent_config["model"],
                messages=openai_messages,
                temperature=agent_config["temperature"],
                max_tokens=agent_config["max_tokens"]
            )
        except AuthenticationError as e:
            # Should not happen (first call would have failed), but handle gracefully
            assistant_content = (
                "I executed the requested task operation, but I'm unable to generate a natural language response "
                "because the OpenAI API key is not properly configured. Your task operation was still completed successfully."
            )
            
            # Store fallback message
            try:
                assistant_message = Message(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role="assistant",
                    content=assistant_content
                )
                session.add(assistant_message)
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)
                session.commit()
            except Exception as db_error:
                raise DatabaseError() from db_error
            
            return {
                "conversation_id": conversation.id,
                "response": assistant_content,
                "tool_calls": tool_calls_made
            }
        except RateLimitError as e:
            raise OpenAIAPIError(retry_after=60) from e
        except APIConnectionError as e:
            raise OpenAIAPIError(retry_after=30) from e
        except APIError as e:
            raise OpenAIAPIError(retry_after=15) from e
        
        assistant_content = final_response.choices[0].message.content
    else:
        # No tools called, use direct response
        assistant_content = message_response.content
    
    try:
        # Step 8: Store assistant response in database
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role="assistant",
            content=assistant_content
        )
        session.add(assistant_message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        
        session.commit()
    except Exception as e:
        raise DatabaseError() from e
    
    # Step 9: Return response
    return {
        "conversation_id": conversation.id,
        "response": assistant_content,
        "tool_calls": tool_calls_made
    }
