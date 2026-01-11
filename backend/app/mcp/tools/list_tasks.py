"""
List Tasks MCP Tool - Retrieves tasks with optional filters.
Stateless function that queries database for user's tasks.
"""
from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from app.models.task import Task
from app.mcp.errors import InvalidUserIdError, ValidationError, DatabaseError, create_empty_list_response


async def list_tasks(session: Session, user_id: str, status: Optional[str] = None) -> Dict[str, Any]:
    """
    List user's tasks with optional status filter.
    
    Args:
        session: Database session (injected dependency)
        user_id: The ID of the user
        status: Filter by status - "all", "pending", or "completed"
        
    Returns:
        Dictionary with tasks list, count, and status
        
    Raises:
        InvalidUserIdError: If user_id is invalid
        ValidationError: If status is invalid
        DatabaseError: If database operation fails
    """
    # Validation
    if not user_id or not user_id.strip():
        raise InvalidUserIdError()
    
    # Normalize status
    if not status:
        status = "all"
    status = status.lower().strip()
    
    if status not in ["all", "pending", "completed"]:
        raise ValidationError("status", "must be 'all', 'pending', or 'completed'")
    
    # Query database
    try:
            # Build query
            statement = select(Task).where(Task.user_id == user_id.strip())
            
            # Apply status filter
            if status == "pending":
                statement = statement.where(Task.completed == False)
            elif status == "completed":
                statement = statement.where(Task.completed == True)
            
            # Order by: incomplete first, then by created_at descending
            statement = statement.order_by(Task.completed.asc(), Task.created_at.desc())
            
            # Execute query
            tasks = session.exec(statement).all()
            
            # Handle empty list (not an error)
            if not tasks:
                return create_empty_list_response(status)
            
            # Format results
            task_list = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed
                }
                for task in tasks
            ]
            
            return {
                "tasks": task_list,
                "count": len(task_list),
                "status": status
            }
    except Exception as e:
        # Catch database errors
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            raise DatabaseError()
        raise
