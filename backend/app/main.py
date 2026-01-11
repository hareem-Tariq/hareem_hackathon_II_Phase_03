"""
FastAPI Main Application - AI-Powered Todo Chatbot Backend.
Stateless backend with OpenAI Agents and MCP tools.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, select

from app.database import init_db, engine
from app.routes import chat_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup: Check database connectivity
    try:
        logger.info("Checking database connectivity...")
        with Session(engine) as session:
            # Execute a simple query to test connection
            session.exec(select(1))
        logger.info("✓ Database connection successful")
    except Exception as e:
        # Sanitize error message to avoid exposing credentials
        error_msg = str(e).split('@')[0] if '@' in str(e) else str(e)
        logger.error(f"✗ Database connection failed: {error_msg}")
        logger.error("Server will start but database operations may fail")
    
    # Initialize database tables
    try:
        logger.info("Initializing database tables...")
        init_db()
        logger.info("✓ Database tables initialized")
    except Exception as e:
        # Sanitize error message to avoid exposing credentials
        error_msg = str(e).split('@')[0] if '@' in str(e) else str(e)
        logger.error(f"✗ Database initialization failed: {error_msg}")
    
    yield
    # Shutdown: Cleanup if needed
    logger.info("Shutting down application...")
    pass


# Create FastAPI app
app = FastAPI(
    title="AI Todo Chatbot API",
    description="Conversational AI interface for task management using OpenAI Agents and MCP",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-phi-ruby-64.vercel.app",
        "http://localhost:3000",
        "http://localhost:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-OpenAI-Domain-Key"],
)

# Register routes
app.include_router(chat_router)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "online",
        "service": "AI Todo Chatbot API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
