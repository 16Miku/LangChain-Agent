# ============================================================
# Chat Service - Configuration
# ============================================================

import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Chat Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./chat.db"

    # JWT Configuration (for validating tokens from auth-service)
    JWT_SECRET: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    # Auth Service URL (for validating users)
    AUTH_SERVICE_URL: str = "http://localhost:8001"

    # LLM Configuration
    GOOGLE_API_KEY: str = ""
    GOOGLE_MODEL: str = "gemini-2.0-flash-lite"

    # OpenAI Compatible Mode
    LLM_PROVIDER: str = "google"  # "google" or "openai_compatible"
    OPENAI_BASE_URL: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # MCP Tools Configuration
    BRIGHT_DATA_API_KEY: str = ""
    PAPER_SEARCH_API_KEY: str = ""

    # E2B Configuration
    E2B_API_KEY: str = ""

    # Data Directory (for persistence)
    DATA_DIR: str = "/tmp/data"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8001",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
