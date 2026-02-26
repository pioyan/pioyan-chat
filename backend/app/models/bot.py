"""Bot Pydantic models for coding bots with container support."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class BotStatus(StrEnum):
    """Bot lifecycle status."""

    registered = "registered"
    building = "building"
    ready = "ready"
    error = "error"


class BotCreate(BaseModel):
    """Payload for registering a new coding bot."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class BotPublic(BaseModel):
    """Public representation of a bot."""

    id: str
    name: str
    description: str | None = None
    owner_id: str
    container_file_name: str
    status: BotStatus = BotStatus.registered
    created_at: datetime
