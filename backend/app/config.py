"""
Configuration management for the application.
Loads settings from environment variables.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str
    
    # OpenAI Configuration (optional - graceful degradation if missing)
    openai_api_key: str = ""
    
    # Application Configuration
    env: str = "development"
    debug: bool = True
    
    # Better Auth Configuration (optional)
    auth_secret: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
