"""
Delete Task MCP Tool - Permanently removes tasks from database.
Stateless function that deletes task from database.
"""
from typing import Dict, Any
from sqlmodel import Session, select
from app.models.task import Task
from app.mcp.errors import InvalidUserIdError, InvalidTaskIdError, TaskNotFoundError, DatabaseError, create_success_response


async def delete_task(session: Session, user_id: str, task_id: int) -> Dict[str, Any]:
    """
    Delete a task permanently.
    
    Args:
        session: Database session (injected dependency)
        user_id: The ID of the user
        task_id: The ID of the task to delete
        
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
    
    # Delete task from database
    try:
            # Find task
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id.strip()
            )
            task = session.exec(statement).first()
            
            if not task:
                raise TaskNotFoundError(task_id)
            
            # Store title for response
            title = task.title
            
            # Delete task
            session.delete(task)
            session.commit()
            
            return create_success_response(
                task_id=task_id,
                status="deleted",
                title=title
            )
    except (TaskNotFoundError, InvalidTaskIdError, InvalidUserIdError):
        raise
    except Exception as e:
        # Catch database errors
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            raise DatabaseError()
        raise
