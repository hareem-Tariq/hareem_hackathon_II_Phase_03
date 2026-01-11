"""
Message Model - SQLModel schema for conversation history.
Stores individual messages (user and assistant) within conversations.
"""
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    """
    Message model for storing conversation history.
    
    Attributes:
        id: Auto-incrementing primary key
        conversation_id: Foreign key to conversations table (indexed)
        user_id: Owner of the message (indexed for security)
        role: Message role - either "user" or "assistant"
        content: Message text content
        created_at: Timestamp of message creation (indexed for chronological ordering)
    """
    __tablename__ = "messages"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True, nullable=False)
    role: str = Field(nullable=False)  # "user" or "assistant"
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    class Config:
        """SQLModel configuration."""
        json_schema_extra = {
            "example": {
                "conversation_id": 1,
                "user_id": "user123",
                "role": "user",
                "content": "Add a task to buy groceries"
            }
        }
