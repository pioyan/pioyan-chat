"""Tests for user/channel/message/agent/task/container Pydantic models."""

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


# ── Agent models ──────────────────────────────────────────────


class TestAgentModels:
    """Tests for Agent Pydantic models."""

    def test_agent_source_enum_values(self):
        from app.models.agent import AgentSource

        assert AgentSource.repo == "repo"
        assert AgentSource.manual == "manual"

    def test_agent_status_enum_values(self):
        from app.models.agent import AgentStatus

        assert AgentStatus.registered == "registered"
        assert AgentStatus.ready == "ready"
        assert AgentStatus.error == "error"

    def test_agent_create_minimal(self):
        from app.models.agent import AgentCreate

        agent = AgentCreate(name="coder")
        assert agent.name == "coder"
        assert agent.description is None
        assert agent.system_prompt is None

    def test_agent_create_full(self):
        from app.models.agent import AgentCreate

        agent = AgentCreate(
            name="reviewer",
            description="Reviews pull requests",
            system_prompt="You are a code reviewer.",
        )
        assert agent.name == "reviewer"
        assert agent.description == "Reviews pull requests"
        assert agent.system_prompt == "You are a code reviewer."

    def test_agent_create_name_too_long(self):
        from app.models.agent import AgentCreate

        with pytest.raises(ValidationError):
            AgentCreate(name="x" * 101)

    def test_agent_create_name_empty(self):
        from app.models.agent import AgentCreate

        with pytest.raises(ValidationError):
            AgentCreate(name="")

    def test_agent_create_description_too_long(self):
        from app.models.agent import AgentCreate

        with pytest.raises(ValidationError):
            AgentCreate(name="bot", description="x" * 1001)

    def test_agent_create_system_prompt_max_length(self):
        from app.models.agent import AgentCreate

        with pytest.raises(ValidationError):
            AgentCreate(name="bot", system_prompt="x" * 10001)

    def test_agent_public_fields(self):
        from datetime import UTC, datetime

        from app.models.agent import AgentPublic, AgentSource, AgentStatus

        agent = AgentPublic(
            id="abc123",
            name="coder",
            description="Writes code",
            system_prompt="You are a coder.",
            source=AgentSource.manual,
            repo_agent_path=None,
            status=AgentStatus.ready,
            owner_id="user1",
            created_at=datetime.now(UTC),
        )
        assert agent.id == "abc123"
        assert agent.source == "manual"
        assert agent.status == "ready"

    def test_agent_public_repo_source(self):
        from datetime import UTC, datetime

        from app.models.agent import AgentPublic, AgentSource, AgentStatus

        agent = AgentPublic(
            id="abc123",
            name="feature-builder",
            source=AgentSource.repo,
            repo_agent_path=".github/agents/feature-builder.md",
            status=AgentStatus.registered,
            owner_id="user1",
            created_at=datetime.now(UTC),
        )
        assert agent.source == "repo"
        assert agent.repo_agent_path == ".github/agents/feature-builder.md"

    def test_agent_public_defaults(self):
        from datetime import UTC, datetime

        from app.models.agent import AgentPublic

        agent = AgentPublic(
            id="abc123",
            name="bot",
            owner_id="user1",
            created_at=datetime.now(UTC),
        )
        assert agent.description is None
        assert agent.system_prompt is None
        assert agent.source == "manual"
        assert agent.repo_agent_path is None
        assert agent.status == "registered"


# ── CodingTask models ────────────────────────────────────────


class TestCodingTaskModels:
    """Tests for CodingTask Pydantic models."""

    def test_task_status_enum_values(self):
        from app.models.coding_task import TaskStatus

        assert TaskStatus.pending == "pending"
        assert TaskStatus.running == "running"
        assert TaskStatus.completed == "completed"
        assert TaskStatus.failed == "failed"

    def test_coding_task_create(self):
        from app.models.coding_task import CodingTaskCreate

        task = CodingTaskCreate(instruction="Add a login button")
        assert task.instruction == "Add a login button"
        assert task.agent_id is None

    def test_coding_task_create_with_agent(self):
        from app.models.coding_task import CodingTaskCreate

        task = CodingTaskCreate(
            instruction="Fix the bug",
            agent_id="agent123",
        )
        assert task.agent_id == "agent123"

    def test_coding_task_create_empty_instruction(self):
        from app.models.coding_task import CodingTaskCreate

        with pytest.raises(ValidationError):
            CodingTaskCreate(instruction="")

    def test_coding_task_create_instruction_too_long(self):
        from app.models.coding_task import CodingTaskCreate

        with pytest.raises(ValidationError):
            CodingTaskCreate(instruction="x" * 10001)

    def test_coding_task_public_fields(self):
        from datetime import UTC, datetime

        from app.models.coding_task import CodingTaskPublic, TaskStatus

        task = CodingTaskPublic(
            id="task1",
            channel_id="ch1",
            agent_id="agent1",
            user_id="user1",
            instruction="Write a test",
            status=TaskStatus.completed,
            result_summary="Done. Created test_foo.py",
            commit_sha="abc123",
            pr_url="https://github.com/owner/repo/pull/1",
            branch_name="feat/test",
            created_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
        )
        assert task.status == "completed"
        assert task.pr_url == "https://github.com/owner/repo/pull/1"

    def test_coding_task_public_defaults(self):
        from datetime import UTC, datetime

        from app.models.coding_task import CodingTaskPublic

        task = CodingTaskPublic(
            id="task1",
            channel_id="ch1",
            agent_id="agent1",
            user_id="user1",
            instruction="Write code",
            created_at=datetime.now(UTC),
        )
        assert task.status == "pending"
        assert task.result_summary is None
        assert task.commit_sha is None
        assert task.pr_url is None
        assert task.branch_name is None
        assert task.completed_at is None


# ── AgentContainer models ────────────────────────────────────


class TestAgentContainerModels:
    """Tests for AgentContainer Pydantic models."""

    def test_container_status_enum_values(self):
        from app.models.agent_container import ContainerStatus

        assert ContainerStatus.creating == "creating"
        assert ContainerStatus.running == "running"
        assert ContainerStatus.stopped == "stopped"
        assert ContainerStatus.error == "error"

    def test_agent_container_public_fields(self):
        from datetime import UTC, datetime

        from app.models.agent_container import AgentContainerPublic, ContainerStatus

        container = AgentContainerPublic(
            id="c1",
            agent_id="agent1",
            channel_id="ch1",
            container_id="docker_abc123",
            status=ContainerStatus.running,
            repo_branch="feat/implement-login",
            created_at=datetime.now(UTC),
            last_active_at=datetime.now(UTC),
        )
        assert container.container_id == "docker_abc123"
        assert container.status == "running"
        assert container.repo_branch == "feat/implement-login"

    def test_agent_container_public_defaults(self):
        from datetime import UTC, datetime

        from app.models.agent_container import AgentContainerPublic

        container = AgentContainerPublic(
            id="c1",
            agent_id="agent1",
            channel_id="ch1",
            created_at=datetime.now(UTC),
        )
        assert container.container_id is None
        assert container.status == "creating"
        assert container.repo_branch is None
        assert container.last_active_at is None


# ── Channel model extensions ─────────────────────────────────


class TestChannelModelExtensions:
    """Tests for Channel model coding extensions."""

    def test_channel_public_coding_fields(self):
        from datetime import UTC, datetime

        from app.models.channel import ChannelPublic

        ch = ChannelPublic(
            id="ch1",
            name="my-project",
            is_coding=True,
            repo_url="https://github.com/owner/repo",
            repo_owner="owner",
            repo_name="repo",
            default_branch="main",
            assigned_agents=["agent1", "agent2"],
            created_by="user1",
            created_at=datetime.now(UTC),
        )
        assert ch.is_coding is True
        assert ch.repo_url == "https://github.com/owner/repo"
        assert ch.repo_owner == "owner"
        assert ch.repo_name == "repo"
        assert ch.default_branch == "main"
        assert ch.assigned_agents == ["agent1", "agent2"]

    def test_channel_public_coding_defaults(self):
        from datetime import UTC, datetime

        from app.models.channel import ChannelPublic

        ch = ChannelPublic(
            id="ch1",
            name="general",
            created_by="user1",
            created_at=datetime.now(UTC),
        )
        assert ch.is_coding is False
        assert ch.repo_url is None
        assert ch.repo_owner is None
        assert ch.repo_name is None
        assert ch.default_branch == "main"
        assert ch.assigned_agents == []

    def test_coding_channel_create(self):
        from app.models.channel import CodingChannelCreate

        ch = CodingChannelCreate(
            name="my-project",
            repo_url="https://github.com/owner/repo",
        )
        assert ch.name == "my-project"
        assert ch.repo_url == "https://github.com/owner/repo"

    def test_coding_channel_create_invalid_url(self):
        from app.models.channel import CodingChannelCreate

        with pytest.raises(ValidationError):
            CodingChannelCreate(
                name="my-project",
                repo_url="not-a-github-url",
            )

    def test_coding_channel_create_with_description(self):
        from app.models.channel import CodingChannelCreate

        ch = CodingChannelCreate(
            name="my-project",
            description="A coding project",
            repo_url="https://github.com/owner/repo",
            default_branch="develop",
        )
        assert ch.description == "A coding project"
        assert ch.default_branch == "develop"
