"""Tests for user/channel/message Pydantic models."""

import pytest
from pydantic import ValidationError

from app.models.channel import ChannelCreate, ChannelUpdate
from app.models.message import MessageCreate
from app.models.user import UserCreate


class TestUserModel:
    def test_valid_user_create(self):
        user = UserCreate(
            username="alice",
            email="alice@example.com",
            password="securepass",
        )
        assert user.username == "alice"
        assert user.email == "alice@example.com"

    def test_username_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(username="a", email="a@example.com", password="pass1234")

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(username="alice", email="a@example.com", password="short")

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(username="alice", email="not-an-email", password="pass1234")


class TestChannelModel:
    def test_valid_channel_create(self):
        ch = ChannelCreate(name="general", description="General channel")
        assert ch.name == "general"
        assert ch.is_private is False

    def test_channel_name_too_long(self):
        with pytest.raises(ValidationError):
            ChannelCreate(name="a" * 81)

    def test_channel_update_partial(self):
        update = ChannelUpdate(name="new-name")
        assert update.name == "new-name"
        assert update.description is None


class TestMessageModel:
    def test_valid_message_create(self):
        msg = MessageCreate(content="Hello!")
        assert msg.content == "Hello!"

    def test_message_empty_content(self):
        with pytest.raises(ValidationError):
            MessageCreate(content="")

    def test_message_too_long(self):
        with pytest.raises(ValidationError):
            MessageCreate(content="a" * 4001)
