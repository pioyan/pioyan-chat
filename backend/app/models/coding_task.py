"""CodingTask Pydantic models for tracking coding instructions."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    """Coding task lifecycle status."""

    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class CodingTaskCreate(BaseModel):
    """Payload for submitting a coding instruction."""

    instruction: str = Field(..., min_length=1, max_length=10000)
    agent_id: str | None = None


class CodingTaskPublic(BaseModel):
    """Public representation of a coding task."""

    id: str
    channel_id: str
    agent_id: str
    user_id: str
    instruction: str
    status: TaskStatus = TaskStatus.pending
    result_summary: str | None = None
    commit_sha: str | None = None
    pr_url: str | None = None
    branch_name: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
