"""
Main entry point for the backend application.
Can be run directly with: python main.py
"""
from app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
