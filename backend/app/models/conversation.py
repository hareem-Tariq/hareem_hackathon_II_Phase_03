"""
Conversation Model - SQLModel schema for chat sessions.
Represents a conversation thread between user and AI assistant.
"""
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """
    Conversation model for storing chat sessions.
    
    Attributes:
        id: Auto-incrementing primary key (conversation_id in API)
        user_id: Owner of the conversation (indexed for fast lookup)
        created_at: Timestamp of conversation start
        updated_at: Timestamp of last message
    """
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """SQLModel configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "user123"
            }
        }
