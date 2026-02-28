"""Agent Pydantic models for AI coding agents."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AgentSource(StrEnum):
    """How the agent was registered."""

    repo = "repo"
    manual = "manual"


class AgentStatus(StrEnum):
    """Agent lifecycle status."""

    registered = "registered"
    ready = "ready"
    error = "error"


class AgentCreate(BaseModel):
    """Payload for creating a new coding agent."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    system_prompt: str | None = Field(default=None, max_length=10000)


class AgentPublic(BaseModel):
    """Public representation of an agent."""

    id: str
    name: str
    description: str | None = None
    system_prompt: str | None = None
    source: AgentSource = AgentSource.manual
    repo_agent_path: str | None = None
    status: AgentStatus = AgentStatus.registered
    owner_id: str
    created_at: datetime
