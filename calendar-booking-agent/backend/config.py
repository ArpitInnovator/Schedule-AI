"""Configuration management for the calendar booking agent."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Google Calendar settings
    google_calendar_credentials_path: str = Field(
        default="",
        description="Path to Google service account JSON credentials"
    )
    google_calendar_id: str = Field(
        default="",
        description="Google Calendar ID to manage appointments"
    )
    
    # Google Gemini API
    google_api_key: str = Field(
        default="",
        description="Google API key for Gemini"
    )
    
    # Server settings
    port: int = Field(default=8000, description="Server port")
    host: str = Field(default="0.0.0.0", description="Server host")
    
    # CORS settings
    cors_origins: list[str] = Field(
        default=["http://localhost:8501", "http://localhost:3000", "*"],
        description="Allowed CORS origins"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create a singleton instance
settings = Settings()


def validate_settings():
    """Validate that all required settings are configured."""
    errors = []
    
    if not settings.google_calendar_credentials_path:
        errors.append("GOOGLE_CALENDAR_CREDENTIALS_PATH is not set")
    elif not Path(settings.google_calendar_credentials_path).exists():
        errors.append(f"Service account file not found: {settings.google_calendar_credentials_path}")
    
    if not settings.google_calendar_id:
        errors.append("GOOGLE_CALENDAR_ID is not set")
    
    if not settings.google_api_key:
        errors.append("GOOGLE_API_KEY is not set")
    
    if errors:
        error_msg = "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        raise ValueError(error_msg)
    
    return True