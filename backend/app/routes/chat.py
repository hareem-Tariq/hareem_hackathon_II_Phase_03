"""
Chat API Route - Single endpoint for conversational task management.
Stateless endpoint that processes messages through OpenAI Agent.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from app.schemas.chat import ChatRequest, ChatResponse
from app.agent import process_chat_message
from app.dependencies import get_db_session
from app.models.conversation import Conversation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.get("/{user_id}/conversations")
async def get_conversations(user_id: str, db: Session = Depends(get_db_session)):
    """
    Get all conversations for a user, sorted by most recent.
    
    Args:
        user_id: The ID of the user
        db: Database session (injected dependency)
        
    Returns:
        List of conversations with id, created_at, updated_at, and preview
    """
    try:
        from app.models.message import Message
        
        statement = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc())
        
        conversations = db.exec(statement).all()
        
        result = []
        for conv in conversations:
            # Get first user message for preview
            message_statement = select(Message).where(
                Message.conversation_id == conv.id,
                Message.role == "user"
            ).order_by(Message.created_at.asc()).limit(1)
            
            first_message = db.exec(message_statement).first()
            preview = first_message.content if first_message else "New conversation"
            
            # Truncate preview if too long
            if len(preview) > 50:
                preview = preview[:50] + "..."
            
            result.append({
                "id": conv.id,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "preview": preview
            })
        
        return {"conversations": result}
        
    except Exception as e:
        logger.error(f"Error fetching conversations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversations: {str(e)}"
        )


@router.delete("/{user_id}/conversations/{conversation_id}")
async def delete_conversation(user_id: str, conversation_id: int, db: Session = Depends(get_db_session)):
    """
    Delete a specific conversation and all its messages.
    
    Args:
        user_id: The ID of the user
        conversation_id: The ID of the conversation to delete
        db: Database session (injected dependency)
        
    Returns:
        Success message
    """
    try:
        from app.models.message import Message
        
        # Get conversation
        conversation = db.get(Conversation, conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Delete all messages in conversation
        message_statement = select(Message).where(Message.conversation_id == conversation_id)
        messages = db.exec(message_statement).all()
        for message in messages:
            db.delete(message)
        
        # Delete conversation
        db.delete(conversation)
        db.commit()
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation: {str(e)}"
        )


@router.delete("/{user_id}/conversations")
async def delete_all_conversations(user_id: str, db: Session = Depends(get_db_session)):
    """
    Delete all conversations for a user.
    
    Args:
        user_id: The ID of the user
        db: Database session (injected dependency)
        
    Returns:
        Success message with count
    """
    try:
        from app.models.message import Message
        
        # Get all user conversations
        conv_statement = select(Conversation).where(Conversation.user_id == user_id)
        conversations = db.exec(conv_statement).all()
        
        deleted_count = 0
        for conversation in conversations:
            # Delete all messages in conversation
            message_statement = select(Message).where(Message.conversation_id == conversation.id)
            messages = db.exec(message_statement).all()
            for message in messages:
                db.delete(message)
            
            # Delete conversation
            db.delete(conversation)
            deleted_count += 1
        
        db.commit()
        
        return {
            "message": f"All conversations deleted successfully",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error deleting all conversations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting all conversations: {str(e)}"
        )


@router.delete("/{user_id}/reset")
async def reset_all_data(user_id: str, db: Session = Depends(get_db_session)):
    """
    RESET ENDPOINT: Delete ALL user data (conversations, messages, tasks).
    This resets the application to a completely fresh state.
    
    Args:
        user_id: The ID of the user
        db: Database session (injected dependency)
        
    Returns:
        Success message with deletion counts
    """
    try:
        from app.models.message import Message
        from app.models.task import Task
        
        # Count for response
        conversations_deleted = 0
        messages_deleted = 0
        tasks_deleted = 0
        
        # 1. Delete all messages (must be first due to foreign key)
        message_statement = select(Message).where(Message.user_id == user_id)
        messages = db.exec(message_statement).all()
        for message in messages:
            db.delete(message)
            messages_deleted += 1
        
        # 2. Delete all conversations
        conv_statement = select(Conversation).where(Conversation.user_id == user_id)
        conversations = db.exec(conv_statement).all()
        for conversation in conversations:
            db.delete(conversation)
            conversations_deleted += 1
        
        # 3. Delete all tasks
        task_statement = select(Task).where(Task.user_id == user_id)
        tasks = db.exec(task_statement).all()
        for task in tasks:
            db.delete(task)
            tasks_deleted += 1
        
        # Commit all deletions
        db.commit()
        
        logger.info(f"Reset completed for user {user_id}: {conversations_deleted} conversations, {messages_deleted} messages, {tasks_deleted} tasks deleted")
        
        return {
            "message": "All data reset successfully",
            "conversations_deleted": conversations_deleted,
            "messages_deleted": messages_deleted,
            "tasks_deleted": tasks_deleted
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error resetting user data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting user data: {str(e)}"
        )


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(user_id: str, request: ChatRequest, db: Session = Depends(get_db_session)):
    """
    Process a chat message and return AI response.
    
    This endpoint:
    1. Loads conversation history from database (or creates new)
    2. Processes message through OpenAI Agent with MCP tools
    3. Saves conversation state back to database
    4. Returns assistant response
    
    Args:
        user_id: The ID of the user (from path)
        request: Chat request with message and optional conversation_id
        db: Database session (injected dependency)
        
    Returns:
        ChatResponse with conversation_id, response, and tool_calls
    """
    try:
        result = await process_chat_message(
            session=db,
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(**result)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )
