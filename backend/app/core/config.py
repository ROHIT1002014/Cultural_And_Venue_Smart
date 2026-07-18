import os
from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Production-ready centralized settings using pydantic-settings with OWASP validation."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = Field(default="Cultural & Venue Smart Copilot Platform")
    ENVIRONMENT: Literal["development", "testing", "staging", "production"] = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    ALLOWED_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:80")

    # Database & Redis Settings
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:password@localhost:5432/cultural_copilot")
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_PASSWORD: str | None = Field(default=None)

    # Security & JWT Configuration
    JWT_SECRET_KEY: str = Field(default="super_secret_development_jwt_key_that_is_long_and_secure_64_bytes")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # AI Providers Configuration
    OPENAI_API_KEY: str = Field(default="sk-mock-openai-key")
    GEMINI_API_KEY: str = Field(default="AIzaSy-mock-gemini-key")
    DEFAULT_AI_PROVIDER: Literal["gemini", "openai"] = Field(default="gemini")
    FALLBACK_AI_PROVIDER: Literal["gemini", "openai"] = Field(default="openai")

    # Environment & Secrets Validator (OWASP Check)
    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret(cls, value: str, info: Any) -> str:
        """Validate that the JWT secret is sufficiently long and high-entropy."""
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production" and (len(value) < 32 or "secret" in value.lower() or "test" in value.lower()):
            raise ValueError("In production, JWT_SECRET_KEY must be at least 32 characters long and high entropy.")
        return value

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_db_url(cls, value: str) -> str:
        """Ensure asyncpg driver is specified for async SQLAlchemy 2.0 ORM."""
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached instance of application settings."""
    return Settings()
