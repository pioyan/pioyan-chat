"""Channel Pydantic models."""

from datetime import datetime

from pydantic import BaseModel, Field


class ChannelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    description: str | None = None
    is_private: bool = False


class ChannelCreate(ChannelBase):
    pass


class ChannelUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=80)
    description: str | None = None


class ChannelPublic(ChannelBase):
    id: str
    is_direct: bool = False
    members: list[str] = []
    created_by: str
    created_at: datetime
