"""
MCP Tool Error Utilities - Standardized user-facing error responses.
Provides friendly, non-technical error messages safe to show users.

All error messages are:
- Human-readable (conversational tone)
- Non-technical (no jargon or implementation details)
- Safe for users (no sensitive information exposed)
- Actionable (includes helpful suggestions)
"""
from typing import Optional, Dict, Any, List


class MCPError(Exception):
    """
    Base exception for MCP tool errors with user-friendly messaging.
    
    All messages are written in conversational, non-technical language
    suitable for direct display to end users.
    """
    
    def __init__(self, error_code: str, message: str, suggestion: str, **kwargs):
        """
        Initialize structured error.
        
        Args:
            error_code: Machine-readable error code (UPPERCASE_SNAKE_CASE)
            message: User-friendly message in conversational tone
            suggestion: Actionable next step the user can take
            **kwargs: Additional error context (sanitized for user safety)
        """
        self.error_code = error_code
        self.message = message
        self.suggestion = suggestion
        self.context = kwargs
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error to dictionary format for API responses.
        
        Returns sanitized error information safe for user display.
        """
        result = {
            "error_code": self.error_code,
            "message": self.message,
            "suggestion": self.suggestion
        }
        # Add any additional context (already sanitized)
        if self.context:
            result.update(self.context)
        return result


class TaskNotFoundError(MCPError):
    """
    Task does not exist or doesn't belong to user.
    
    User-friendly message: "I couldn't find that task."
    """
    
    def __init__(self, task_id: int, user_hint: Optional[str] = None):
        hint = f" {user_hint}" if user_hint else ""
        super().__init__(
            error_code="TASK_NOT_FOUND",
            message=f"I couldn't find task #{task_id}.{hint} Would you like to see your current tasks?",
            suggestion="Try 'show my tasks' to see what's on your list.",
            task_id=task_id
        )


class InvalidTaskIdError(MCPError):
    """
    Invalid task ID format or value.
    
    User-friendly message: "That doesn't look like a valid task number."
    """
    
    def __init__(self, task_id: Any):
        super().__init__(
            error_code="INVALID_TASK_ID",
            message=f"That doesn't look like a valid task number. I need a number like 1, 2, or 42.",
            suggestion="Try using just the task number (like 'complete 5').",
            provided_value=str(task_id)
        )


class InvalidUserIdError(MCPError):
    """
    Invalid or missing user ID.
    
    User-friendly message: Technical issue, please reconnect.
    """
    
    def __init__(self):
        super().__init__(
            error_code="INVALID_USER_ID",
            message="There seems to be an issue with your session.",
            suggestion="Please refresh the page or log in again."
        )


class ValidationError(MCPError):
    """
    Generic validation error for user input.
    
    User-friendly message: Explains what's wrong in plain language.
    """
    
    def __init__(self, field: str, reason: str):
        # Make reason more user-friendly
        friendly_reason = reason.replace("is required", "can't be empty")
        friendly_reason = friendly_reason.replace("must be", "needs to be")
        
        super().__init__(
            error_code="VALIDATION_ERROR",
            message=f"There's an issue with the {field}: {friendly_reason}.",
            suggestion=f"Please check your {field} and try again.",
            field=field
        )


class EmptyTaskListError(MCPError):
    """
    User has no tasks matching the criteria.
    
    This is technically not an error but a successful empty result.
    Included here for consistency in messaging.
    """
    
    def __init__(self, filter_status: str = "all"):
        status_text = {
            "all": "any",
            "pending": "pending",
            "completed": "completed"
        }.get(filter_status, "any")
        
        super().__init__(
            error_code="EMPTY_TASK_LIST",
            message=f"Great news! You don't have any {status_text} tasks. You're all caught up!",
            suggestion="Would you like to add a new task? Just say 'add [task name]' or 'help' for more options.",
            status=filter_status
        )


class MultipleTasksMatchError(MCPError):
    """
    Multiple tasks match the user's query - clarification needed.
    
    User-friendly message: Shows numbered list and asks which one.
    """
    
    def __init__(self, query: str, matches: List[Dict[str, Any]], action: str):
        # Build friendly numbered list
        match_list = "\n".join([
            f"  {i+1}. Task #{task['id']}: {task['title']}"
            for i, task in enumerate(matches)
        ])
        
        super().__init__(
            error_code="MULTIPLE_MATCHES",
            message=f"I found {len(matches)} tasks matching '{query}':\n{match_list}\n\nWhich one would you like to {action}?",
            suggestion="Tell me the number or give me more details about which task you mean.",
            query=query,
            match_count=len(matches),
            matches=matches
        )


class DatabaseError(MCPError):
    """
    Temporary database connection or query error.
    
    User-friendly message: Temporary issue, try again soon.
    """
    
    def __init__(self, support_id: Optional[str] = None):
        super().__init__(
            error_code="DATABASE_UNAVAILABLE",
            message="I'm having trouble connecting to your task list right now. This is temporary!",
            suggestion="Please wait a moment and try again. If this keeps happening, let us know.",
            retry_after_seconds=30,
            support_reference=support_id or "temp_error"
        )


class OpenAIAPIError(MCPError):
    """
    Temporary OpenAI API failure.
    
    User-friendly message: AI temporarily unavailable, retry.
    """
    
    def __init__(self, retry_after: int = 5):
        super().__init__(
            error_code="AI_TEMPORARILY_UNAVAILABLE",
            message="I'm having a moment of difficulty understanding right now. This happens sometimes!",
            suggestion=f"Please try again in a few seconds. Your tasks are safe!",
            retry_after_seconds=retry_after
        )


def sanitize_error_for_user(error: Exception) -> Dict[str, Any]:
    """
    Sanitize any exception into a safe, user-friendly error response.
    
    This function ensures that even unexpected errors are presented
    in a friendly, non-technical way that's safe to show users.
    
    Args:
        error: Any exception
        
    Returns:
        User-friendly error dictionary
    """
    if isinstance(error, MCPError):
        # Already user-friendly
        return error.to_dict()
    
    # Convert unexpected errors to generic friendly message
    return {
        "error_code": "UNEXPECTED_ERROR",
        "message": "Oops! Something unexpected happened. Don't worry, your tasks are safe!",
        "suggestion": "Please try again. If this keeps happening, let us know so we can fix it.",
        "error_type": type(error).__name__  # For debugging, but non-revealing
    }


def create_success_response(**kwargs) -> Dict[str, Any]:
    """
    Create standardized success response.
    
    Args:
        **kwargs: Response data fields
        
    Returns:
        Dictionary with response data
    """
    return kwargs


def create_empty_list_response(status: str = "all") -> Dict[str, Any]:
    """
    Create response for empty task list with friendly message.
    
    This is a successful response (not an error) but includes
    a friendly message for the user.
    
    Args:
        status: Filter status used (all/pending/completed)
        
    Returns:
        Empty list with user-friendly message
    """
    status_text = {
        "all": "any",
        "pending": "pending",
        "completed": "completed"
    }.get(status, "any")
    
    return {
        "tasks": [],
        "count": 0,
        "status": status,
        "message": f"You don't have any {status_text} tasks. You're all caught up!",
        "suggestion": "Add a new task by saying 'add [task name]' or say 'help' for more options."
    }
