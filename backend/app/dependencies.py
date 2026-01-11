"""
Shared dependencies for FastAPI routes and services.
Provides reusable dependency injection functions.
"""
from typing import Generator
from sqlmodel import Session
from app.database import get_db

# Re-export get_db for convenience
__all__ = ["get_db_session"]


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    This is the primary dependency for all routes, MCP tools, and agents
    that need database access. It ensures sessions are properly closed
    after use and prevents global session storage.
    
    Usage in FastAPI routes:
        @router.get("/endpoint")
        async def endpoint(db: Session = Depends(get_db_session)):
            # Use db session
            pass
    
    Usage in MCP tools/agents:
        Pass session explicitly as parameter from the calling route
    
    Yields:
        Session: SQLModel database session
    """
    yield from get_db()
