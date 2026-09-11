"""Configuration management using pydantic-settings."""

from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    bot_token: str = Field(..., description="Telegram bot token")
    chat_id: str = Field(..., description="Telegram chat ID")
    allowed_user_ids: str = Field(
        "", description="Comma-separated Telegram user IDs allowed to issue commands"
    )

    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        """Validate bot token format."""
        import re

        if not v:
            raise ValueError("BOT_TOKEN must be set")
        # Telegram bot tokens are numeric:alphanumeric
        if not re.match(r"^[0-9]+:[A-Za-z0-9_-]+$", v):
            raise ValueError("Invalid BOT_TOKEN format")
        return v

    @field_validator("chat_id")
    @classmethod
    def validate_chat_id(cls, v: str) -> str:
        """Validate chat ID format."""
        import re

        if not v:
            raise ValueError("CHAT_ID must be set")
        # Chat ID can be numeric (can be negative for groups)
        if not re.match(r"^-?[0-9]+$", v):
            raise ValueError("Invalid CHAT_ID format")
        return v

    @field_validator("allowed_user_ids")
    @classmethod
    def validate_allowed_user_ids(cls, v: str) -> str:
        """Validate the allowlist is comma-separated numeric user IDs."""
        import re

        if not v.strip():
            return ""
        for part in v.split(","):
            if not re.match(r"^[0-9]+$", part.strip()):
                raise ValueError("ALLOWED_USER_IDS must be comma-separated numeric user IDs")
        return v

    @model_validator(mode="after")
    def validate_authorization_is_resolvable(self) -> Settings:
        """Refuse to start if no sender allowlist can be determined.

        A negative CHAT_ID denotes a group or channel, not a user, so it cannot
        stand in for the owner's user ID. Defaulting there would authorize every
        member of the group, so require an explicit list instead.
        """
        if not self.allowed_user_ids.strip() and self.chat_id.startswith("-"):
            raise ValueError(
                "CHAT_ID is a group/channel ID; ALLOWED_USER_IDS must be set explicitly "
                "so commands are not accepted from every member of the group"
            )
        return self

    @property
    def authorized_user_ids(self) -> set[int]:
        """User IDs permitted to issue commands.

        Defaults to CHAT_ID: in a private chat the chat ID is the owner's own
        user ID, so existing single-user deployments need no new configuration.
        """
        if self.allowed_user_ids.strip():
            return {int(part.strip()) for part in self.allowed_user_ids.split(",") if part.strip()}
        return {int(self.chat_id)}


# Lazy-loaded global settings instance
_settings_instance: Settings | None = None


def _get_settings() -> Settings:
    """Get or create the settings instance (lazy initialization)."""
    global _settings_instance
    if _settings_instance is None:
        # Check if we're in a test environment (pytest sets this)
        import sys

        if "pytest" in sys.modules:
            # In test environment, try to create Settings but catch validation errors
            # Tests should mock settings before accessing attributes
            try:
                _settings_instance = Settings()
            except Exception:
                # If validation fails in test environment, create a mock-like object
                # This allows test collection to proceed; tests should mock settings
                from unittest.mock import MagicMock

                _settings_instance = MagicMock()
        else:
            _settings_instance = Settings()
    return _settings_instance


class _SettingsProxy:
    """Proxy object that lazily loads settings on attribute access."""

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the settings instance."""
        return getattr(_get_settings(), name)


# Global settings proxy (lazy initialization)
settings = _SettingsProxy()
