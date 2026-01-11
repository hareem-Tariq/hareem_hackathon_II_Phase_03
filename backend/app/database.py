"""
Database configuration and session management.
Handles SQLModel engine creation, session factory, and dependency injection.
"""
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import QueuePool
from functools import lru_cache
from typing import Generator

from app.config import get_settings

# Import all models to register them with SQLModel metadata
# This ensures all tables are created by create_all()
from app.models import Task, Conversation, Message


settings = get_settings()

# Create engine with connection pooling optimized for Neon Serverless PostgreSQL
# Neon Serverless requires careful connection management to avoid leaks and timeouts
engine = create_engine(
    settings.database_url,
    echo=settings.debug,             # Logs SQL queries in debug mode (no credentials exposed)
    hide_parameters=True,            # Hide parameter values in SQL logs (security)
    poolclass=QueuePool,
    
    # Connection Pool Settings (Neon Serverless Optimized)
    pool_size=5,                    # Small pool - Neon pooler handles scaling
    max_overflow=5,                 # Limited overflow to prevent connection exhaustion
    pool_pre_ping=True,             # Test connections before use (catch stale connections)
    pool_recycle=300,               # Recycle after 5 min (Neon recommends < 5 min)
    pool_timeout=30,                # Wait max 30s for connection from pool
    
    # Connection Arguments (Neon Serverless Requirements)
    connect_args={
        "sslmode": "require",       # SSL required by Neon
        "connect_timeout": 10,      # Connection timeout (10s recommended)
        "application_name": "todo-chatbot",  # For Neon connection monitoring
    },
    
    # Execution Options (Prevent Long-Lived Transactions)
    execution_options={
        "isolation_level": "READ COMMITTED"  # Neon Serverless default
    }
)


def init_db() -> None:
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    
    Creates tables for:
    - tasks: User todo items
    - conversations: Chat session threads
    - messages: Conversation history
    
    Uses SQLModel.metadata.create_all() which:
    - Creates tables if they don't exist
    - Does NOT drop existing tables
    - Idempotent - safe to call multiple times
    - Works with fresh Neon databases
    """
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection for database sessions.
    Automatically closes session after request completion.
    
    CRITICAL for Neon Serverless:
    - Session auto-closed via context manager (prevents leaks)
    - Transactions kept short (avoid long-lived transactions)
    - Connection returned to pool immediately after use
    - No async - uses sync SQLModel for compatibility
    
    Usage:
        @app.post("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            # Session automatically closed after function returns
            result = db.exec(select(Task)).all()
            return result
    """
    session = Session(engine, expire_on_commit=False)
    try:
        yield session
        session.commit()  # Commit if no exceptions
    except Exception:
        session.rollback()  # Rollback on error
        raise
    finally:
        session.close()  # Always close (prevent connection leaks)
