"""AgentContainer Pydantic models for tracking running containers."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ContainerStatus(StrEnum):
    """Docker container lifecycle status."""

    creating = "creating"
    running = "running"
    stopped = "stopped"
    error = "error"


class AgentContainerPublic(BaseModel):
    """Public representation of an agent container."""

    id: str
    agent_id: str
    channel_id: str
    container_id: str | None = None
    status: ContainerStatus = ContainerStatus.creating
    repo_branch: str | None = None
    created_at: datetime
    last_active_at: datetime | None = None
