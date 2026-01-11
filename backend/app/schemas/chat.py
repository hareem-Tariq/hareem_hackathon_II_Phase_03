"""
Chat API Schemas - Request and response models.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    
    message: str = Field(..., description="User's message", min_length=1)
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID (creates new if not provided)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Add a task to buy groceries",
                "conversation_id": 1
            }
        }


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    
    conversation_id: int = Field(..., description="The conversation ID")
    response: str = Field(..., description="AI assistant's response")
    tool_calls: List[Dict[str, Any]] = Field(default=[], description="List of MCP tools invoked")
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 1,
                "response": "I've added 'Buy groceries' to your task list.",
                "tool_calls": [
                    {
                        "tool": "add_task",
                        "arguments": {"user_id": "user123", "title": "Buy groceries"},
                        "result": {"task_id": 1, "status": "created", "title": "Buy groceries"}
                    }
                ]
            }
        }
