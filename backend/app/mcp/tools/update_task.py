"""
Update Task MCP Tool - Updates existing task properties.
Stateless function that modifies task in database.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from app.models.task import Task
from app.mcp.errors import InvalidUserIdError, InvalidTaskIdError, TaskNotFoundError, ValidationError, DatabaseError, create_success_response


async def update_task(
    session: Session,
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update an existing task's title or description.
    
    Args:
        session: Database session (injected dependency)
        user_id: The ID of the user
        task_id: The ID of the task to update
        title: New title (optional)
        description: New description (optional)
        
    Returns:
        Dictionary with task_id, status, and updated fields
        
    Raises:
        InvalidUserIdError: If user_id is invalid
        InvalidTaskIdError: If task_id is invalid
        TaskNotFoundError: If task not found
        ValidationError: If title or description validation fails
        DatabaseError: If database operation fails
    """
    # Validation
    if not user_id or not user_id.strip():
        raise InvalidUserIdError()
    
    if not task_id or not isinstance(task_id, int) or task_id <= 0:
        raise InvalidTaskIdError(task_id)
    
    if title and len(title) > 200:
        raise ValidationError("title", "must be 200 characters or less")
    
    if description and len(description) > 1000:
        raise ValidationError("description", "must be 1000 characters or less")
    
    # At least one field must be provided
    if title is None and description is None:
        raise ValidationError("update", "at least one of title or description must be provided")
    
    # Update task in database
    try:
        # Find task
        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id.strip()
        )
        task = session.exec(statement).first()
        
        if not task:
            raise TaskNotFoundError(task_id)
        
        # Update fields
        updated_fields = []
        if title is not None:
            task.title = title.strip()
            updated_fields.append("title")
        
        if description is not None:
            task.description = description.strip()
            updated_fields.append("description")
        
        task.updated_at = datetime.utcnow()
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        return create_success_response(
            task_id=task.id,
            status="updated",
            title=task.title,
            updated_fields=updated_fields
        )
    except (TaskNotFoundError, InvalidTaskIdError, InvalidUserIdError, ValidationError):
        raise
    except Exception as e:
        # Catch database errors
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            raise DatabaseError()
        raise
