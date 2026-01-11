"""
Complete Task MCP Tool - Marks tasks as completed or pending.
Stateless function that updates task completion status in database.
"""
from datetime import datetime
from typing import Dict, Any
from sqlmodel import Session, select
from app.models.task import Task
from app.mcp.errors import InvalidUserIdError, InvalidTaskIdError, TaskNotFoundError, DatabaseError, create_success_response


async def complete_task(session: Session, user_id: str, task_id: int, completed: bool = True) -> Dict[str, Any]:
    """
    Mark a task as completed or uncompleted.
    
    Args:
        session: Database session (injected dependency)
        user_id: The ID of the user
        task_id: The ID of the task to complete
        completed: True to mark as completed, False to mark as pending
        
    Returns:
        Dictionary with task_id, status, and title
        
    Raises:
        InvalidUserIdError: If user_id is invalid
        InvalidTaskIdError: If task_id is invalid
        TaskNotFoundError: If task not found
        DatabaseError: If database operation fails
    """
    # Validation
    if not user_id or not user_id.strip():
        raise InvalidUserIdError()
    
    if not task_id or not isinstance(task_id, int) or task_id <= 0:
        raise InvalidTaskIdError(task_id)
    
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
            
            # Update completion status
            task.completed = completed
            task.updated_at = datetime.utcnow()
            
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return create_success_response(
                task_id=task.id,
                status="completed" if completed else "pending",
                title=task.title
            )
    except (TaskNotFoundError, InvalidTaskIdError, InvalidUserIdError):
        raise
    except Exception as e:
        # Catch database errors
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            raise DatabaseError()
        raise
