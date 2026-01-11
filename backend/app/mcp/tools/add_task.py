"""
Add Task MCP Tool - Creates new tasks in the database.
Stateless function that persists task immediately to database.
"""
from datetime import datetime
from typing import Dict, Any
from sqlmodel import Session
from app.models.task import Task
from app.mcp.errors import InvalidUserIdError, ValidationError, DatabaseError, create_success_response


async def add_task(session: Session, user_id: str, title: str, description: str = "") -> Dict[str, Any]:
    """
    Create a new task for the user.
    
    Args:
        session: Database session (injected dependency)
        user_id: The ID of the user creating the task
        title: Task title (required, max 200 chars)
        description: Optional task description (max 1000 chars)
        
    Returns:
        Dictionary with task_id, status, and title
        
    Raises:
        InvalidUserIdError: If user_id is invalid
        ValidationError: If title or description validation fails
        DatabaseError: If database operation fails
    """
    # Validation
    if not user_id or not user_id.strip():
        raise InvalidUserIdError()
    
    if not title or not title.strip():
        raise ValidationError("title", "is required")
    
    if len(title) > 200:
        raise ValidationError("title", "must be 200 characters or less")
    
    if len(description) > 1000:
        raise ValidationError("description", "must be 1000 characters or less")
    
    # Create task in database
    try:
            task = Task(
                user_id=user_id.strip(),
                title=title.strip(),
                description=description.strip() if description else "",
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return create_success_response(
                task_id=task.id,
                status="created",
                title=task.title
            )
    except Exception as e:
        # Catch database errors
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            raise DatabaseError()
        raise
