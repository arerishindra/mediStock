"""
MediStock Backend — Core Configuration

Loads all application settings from environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # Application
    APP_NAME: str = "MediStock"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION-use-a-random-64-char-hex"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "sqlite:///./medistock.db"
    # For MySQL: mysql+pymysql://user:pass@localhost:3306/medistock

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Rate limiting
    LOGIN_RATE_LIMIT_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_WINDOW_MINUTES: int = 15

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
