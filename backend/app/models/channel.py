"""Channel Pydantic models."""

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


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
    is_coding: bool = False
    members: list[str] = []
    # Coding channel fields
    repo_url: str | None = None
    repo_owner: str | None = None
    repo_name: str | None = None
    default_branch: str = "main"
    assigned_agents: list[str] = []
    created_by: str
    created_at: datetime


_GITHUB_REPO_RE = re.compile(r"^https://github\.com/[\w.\-]+/[\w.\-]+$")


class CodingChannelCreate(BaseModel):
    """Payload for creating a coding channel linked to a GitHub repository."""

    name: str = Field(..., min_length=1, max_length=80)
    description: str | None = None
    repo_url: str = Field(...)
    default_branch: str = "main"

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v: str) -> str:
        if not _GITHUB_REPO_RE.match(v):
            raise ValueError(
                "Must be a valid GitHub repository URL (https://github.com/owner/repo)"
            )
        return v
