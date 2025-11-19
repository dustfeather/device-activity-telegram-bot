"""Configuration management using pydantic-settings."""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )

    bot_token: str = Field(..., description="Telegram bot token")
    chat_id: str = Field(..., description="Telegram chat ID")

    @field_validator('bot_token')
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        """Validate bot token format."""
        import re
        if not v:
            raise ValueError("BOT_TOKEN must be set")
        # Telegram bot tokens are numeric:alphanumeric
        if not re.match(r'^[0-9]+:[A-Za-z0-9_-]+$', v):
            raise ValueError("Invalid BOT_TOKEN format")
        return v

    @field_validator('chat_id')
    @classmethod
    def validate_chat_id(cls, v: str) -> str:
        """Validate chat ID format."""
        import re
        if not v:
            raise ValueError("CHAT_ID must be set")
        # Chat ID can be numeric (can be negative for groups)
        if not re.match(r'^-?[0-9]+$', v):
            raise ValueError("Invalid CHAT_ID format")
        return v


# Global settings instance
settings = Settings()

