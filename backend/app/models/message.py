"""Message Pydantic models."""

from datetime import datetime

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=4000)


class MessageCreate(MessageBase):
    file_url: str | None = None


class MessagePublic(MessageBase):
    id: str
    channel_id: str
    sender_id: str
    file_url: str | None = None
    thread_id: str | None = None
    reply_count: int = 0
    created_at: datetime
    updated_at: datetime | None = None
