"""Unit tests for config.py settings validation."""

import pytest
from pydantic import ValidationError

from src.config import Settings


class TestAuthorizedUserIds:
    """Test cases for resolving the command allowlist."""

    def test_defaults_to_chat_id_for_private_chat(self):
        """A positive CHAT_ID is the owner's own user ID, so it needs no extra config."""
        settings = Settings(bot_token="123456789:ABCdef", chat_id="67890")

        assert settings.authorized_user_ids == {67890}

    def test_explicit_allowlist_overrides_chat_id(self):
        settings = Settings(
            bot_token="123456789:ABCdef", chat_id="67890", allowed_user_ids="111, 222"
        )

        assert settings.authorized_user_ids == {111, 222}

    def test_group_chat_id_without_allowlist_is_rejected(self):
        """A negative CHAT_ID is a group; defaulting would authorize every member."""
        with pytest.raises(ValidationError, match="ALLOWED_USER_IDS must be set explicitly"):
            Settings(bot_token="123456789:ABCdef", chat_id="-1001234567890")

    def test_group_chat_id_with_allowlist_is_accepted(self):
        settings = Settings(
            bot_token="123456789:ABCdef", chat_id="-1001234567890", allowed_user_ids="12345"
        )

        assert settings.authorized_user_ids == {12345}

    def test_non_numeric_allowlist_is_rejected(self):
        with pytest.raises(ValidationError, match="comma-separated numeric user IDs"):
            Settings(bot_token="123456789:ABCdef", chat_id="67890", allowed_user_ids="12345,abc")

    def test_negative_user_id_in_allowlist_is_rejected(self):
        """User IDs are positive; a negative value is a chat ID pasted by mistake."""
        with pytest.raises(ValidationError, match="comma-separated numeric user IDs"):
            Settings(bot_token="123456789:ABCdef", chat_id="67890", allowed_user_ids="-100123")
