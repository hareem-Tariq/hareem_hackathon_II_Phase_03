"""
Task Model - SQLModel schema for todo items.
Represents user tasks with title, description, completion status, and timestamps.
"""
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Task model for storing todo items.
    
    Attributes:
        id: Auto-incrementing primary key
        user_id: Owner of the task (indexed for fast lookup)
        title: Task title (required, max 200 chars)
        description: Optional task description (max 1000 chars)
        completed: Completion status (default False, indexed)
        created_at: Timestamp of creation (auto-populated)
        updated_at: Timestamp of last update (auto-populated)
    """
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    title: str = Field(max_length=200, nullable=False)
    description: Optional[str] = Field(default="", max_length=1000)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """SQLModel configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False
            }
        }
