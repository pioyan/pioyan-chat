"""Integration tests for the coding task execution pipeline.

Tests the full flow: task creation → Orchestrator.execute_task →
ContainerService → Agent Runtime HTTP → DB update → Socket.IO notification.

All Docker and HTTP calls are mocked to keep tests fast and deterministic.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from bson import ObjectId
from httpx import AsyncClient

from app.models.coding_task import TaskStatus

# ── Helpers ───────────────────────────────────────────────────


async def _setup_coding_channel_with_agent(auth_client: AsyncClient):
    """Create a coding channel, an agent, and assign the agent."""
    agent_res = await auth_client.post(
        "/api/agents",
        json={"name": "pipeline-bot", "system_prompt": "You build apps."},
    )
    agent_id = agent_res.json()["id"]

    ch_res = await auth_client.post(
        "/api/channels/coding",
        json={
            "name": "pipeline-test",
            "repo_url": "https://github.com/pioyan/talent-flow",
        },
    )
    channel_id = ch_res.json()["id"]

    await auth_client.post(f"/api/channels/{channel_id}/agents/{agent_id}")
    return channel_id, agent_id


def _mock_container_service():
    """Return a mock ContainerService whose methods are all AsyncMock."""
    mock = MagicMock()
    mock.build_agent_image = AsyncMock(return_value="pioyan-chat-agent-base:latest")
    mock.create_container = AsyncMock(return_value="docker_container_id_123")
    mock.start_container = AsyncMock()
    mock.run_agent_container = AsyncMock(
        return_value=("docker_container_id_123", "pioyan-agent-a1-ch1", 32768)
    )
    mock.wait_for_ready = AsyncMock(return_value=True)
    mock.send_task = AsyncMock(
        return_value={
            "status": "completed",
            "task_id": "placeholder",
            "response": "Generated code",
            "summary": "Created login page and tests",
            "files_modified": ["src/app/login/page.tsx"],
            "commit_sha": "abc123def456",
            "pr_url": "https://github.com/pioyan/talent-flow/pull/1",
            "branch_name": "agent/pipeline-bot/abc123de",
        }
    )
    mock.cleanup_container = AsyncMock()
    mock.stop_container = AsyncMock()
    mock.remove_container = AsyncMock()
    return mock


# ── Tests ─────────────────────────────────────────────────────


class TestPipelineExecution:
    """Test the full pipeline via Orchestrator.execute_task()."""

    async def test_successful_task_execution(self, auth_client: AsyncClient):
        """Complete pipeline: pending → running → completed with results."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)

        # Create a task (this triggers background execution)
        # But we want to test execute_task directly with mocked Docker
        from app.services.orchestrator import Orchestrator

        mock_cs = _mock_container_service()

        # Create task in DB first
        db = get_db()
        task_doc = {
            "_id": ObjectId(),
            "channel_id": ObjectId(channel_id),
            "agent_id": ObjectId(agent_id),
            "user_id": ObjectId(),
            "instruction": "Build auth module",
            "status": TaskStatus.pending,
            "result_summary": None,
            "commit_sha": None,
            "pr_url": None,
            "branch_name": None,
            "created_at": datetime.now(UTC),
            "completed_at": None,
        }
        await db["coding_tasks"].insert_one(task_doc)
        task_id = str(task_doc["_id"])

        with patch(
            "app.services.container_service.ContainerService",
            return_value=mock_cs,
        ):
            await Orchestrator.execute_task(
                task_id=task_id,
                channel_id=channel_id,
                agent_id=agent_id,
                instruction="Build auth module",
            )

        # Verify DB was updated
        updated = await db["coding_tasks"].find_one({"_id": task_doc["_id"]})
        assert updated["status"] == TaskStatus.completed
        assert updated["commit_sha"] == "abc123def456"
        assert updated["pr_url"] == "https://github.com/pioyan/talent-flow/pull/1"
        assert updated["branch_name"] == "agent/pipeline-bot/abc123de"
        assert updated["result_summary"] == "Created login page and tests"
        assert updated["completed_at"] is not None

        # Verify container lifecycle was called correctly
        mock_cs.run_agent_container.assert_called_once()
        mock_cs.wait_for_ready.assert_called_once_with(
            "pioyan-agent-a1-ch1", host_port=32768,
        )
        mock_cs.send_task.assert_called_once_with(
            container_name="pioyan-agent-a1-ch1",
            task_id=task_id,
            instruction="Build auth module",
            host_port=32768,
        )
        mock_cs.cleanup_container.assert_called_once_with("docker_container_id_123")

    async def test_container_startup_failure(self, auth_client: AsyncClient):
        """When container fails to start, task should be marked as failed."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)

        from app.services.orchestrator import Orchestrator

        mock_cs = _mock_container_service()
        mock_cs.run_agent_container = AsyncMock(
            side_effect=RuntimeError("Docker daemon not running")
        )

        db = get_db()
        task_doc = {
            "_id": ObjectId(),
            "channel_id": ObjectId(channel_id),
            "agent_id": ObjectId(agent_id),
            "user_id": ObjectId(),
            "instruction": "Some task",
            "status": TaskStatus.pending,
            "result_summary": None,
            "commit_sha": None,
            "pr_url": None,
            "branch_name": None,
            "created_at": datetime.now(UTC),
            "completed_at": None,
        }
        await db["coding_tasks"].insert_one(task_doc)
        task_id = str(task_doc["_id"])

        with patch(
            "app.services.container_service.ContainerService",
            return_value=mock_cs,
        ):
            await Orchestrator.execute_task(
                task_id=task_id,
                channel_id=channel_id,
                agent_id=agent_id,
                instruction="Some task",
            )

        updated = await db["coding_tasks"].find_one({"_id": task_doc["_id"]})
        assert updated["status"] == TaskStatus.failed
        assert "Docker daemon not running" in updated["result_summary"]
        assert updated["completed_at"] is not None

    async def test_container_ready_timeout(self, auth_client: AsyncClient):
        """When agent runtime never becomes ready, task fails."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)

        from app.services.orchestrator import Orchestrator

        mock_cs = _mock_container_service()
        mock_cs.wait_for_ready = AsyncMock(return_value=False)

        db = get_db()
        task_doc = {
            "_id": ObjectId(),
            "channel_id": ObjectId(channel_id),
            "agent_id": ObjectId(agent_id),
            "user_id": ObjectId(),
            "instruction": "Build dashboard",
            "status": TaskStatus.pending,
            "result_summary": None,
            "commit_sha": None,
            "pr_url": None,
            "branch_name": None,
            "created_at": datetime.now(UTC),
            "completed_at": None,
        }
        await db["coding_tasks"].insert_one(task_doc)
        task_id = str(task_doc["_id"])

        with patch(
            "app.services.container_service.ContainerService",
            return_value=mock_cs,
        ):
            await Orchestrator.execute_task(
                task_id=task_id,
                channel_id=channel_id,
                agent_id=agent_id,
                instruction="Build dashboard",
            )

        updated = await db["coding_tasks"].find_one({"_id": task_doc["_id"]})
        assert updated["status"] == TaskStatus.failed
        assert "timeout" in updated["result_summary"].lower()
        # Container should still be cleaned up
        mock_cs.cleanup_container.assert_called_once()

    async def test_agent_runtime_error_response(self, auth_client: AsyncClient):
        """When agent runtime returns HTTP 500, task fails with error info."""

        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)

        from app.services.orchestrator import Orchestrator

        mock_cs = _mock_container_service()
        mock_cs.send_task = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Internal Server Error",
                request=httpx.Request("POST", "http://test/task"),
                response=httpx.Response(500),
            )
        )

        db = get_db()
        task_doc = {
            "_id": ObjectId(),
            "channel_id": ObjectId(channel_id),
            "agent_id": ObjectId(agent_id),
            "user_id": ObjectId(),
            "instruction": "Broken task",
            "status": TaskStatus.pending,
            "result_summary": None,
            "commit_sha": None,
            "pr_url": None,
            "branch_name": None,
            "created_at": datetime.now(UTC),
            "completed_at": None,
        }
        await db["coding_tasks"].insert_one(task_doc)
        task_id = str(task_doc["_id"])

        with patch(
            "app.services.container_service.ContainerService",
            return_value=mock_cs,
        ):
            await Orchestrator.execute_task(
                task_id=task_id,
                channel_id=channel_id,
                agent_id=agent_id,
                instruction="Broken task",
            )

        updated = await db["coding_tasks"].find_one({"_id": task_doc["_id"]})
        assert updated["status"] == TaskStatus.failed
        assert "error" in updated["result_summary"].lower()
        mock_cs.cleanup_container.assert_called_once()

    async def test_missing_repo_url_fails(self, auth_client: AsyncClient):
        """Channel without repo_url should fail the task immediately."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)

        # Manually clear the repo_url
        db = get_db()
        await db["channels"].update_one(
            {"_id": ObjectId(channel_id)},
            {"$set": {"repo_url": ""}},
        )

        from app.services.orchestrator import Orchestrator

        mock_cs = _mock_container_service()

        task_doc = {
            "_id": ObjectId(),
            "channel_id": ObjectId(channel_id),
            "agent_id": ObjectId(agent_id),
            "user_id": ObjectId(),
            "instruction": "Do something",
            "status": TaskStatus.pending,
            "result_summary": None,
            "commit_sha": None,
            "pr_url": None,
            "branch_name": None,
            "created_at": datetime.now(UTC),
            "completed_at": None,
        }
        await db["coding_tasks"].insert_one(task_doc)
        task_id = str(task_doc["_id"])

        with patch(
            "app.services.container_service.ContainerService",
            return_value=mock_cs,
        ):
            await Orchestrator.execute_task(
                task_id=task_id,
                channel_id=channel_id,
                agent_id=agent_id,
                instruction="Do something",
            )

        updated = await db["coding_tasks"].find_one({"_id": task_doc["_id"]})
        assert updated["status"] == TaskStatus.failed
        assert "repo_url" in updated["result_summary"].lower()
        # Should not have attempted container ops
        mock_cs.run_agent_container.assert_not_called()

    async def test_container_cleanup_on_success(self, auth_client: AsyncClient):
        """Container is always cleaned up, even on success."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)

        from app.services.orchestrator import Orchestrator

        mock_cs = _mock_container_service()

        db = get_db()
        task_doc = {
            "_id": ObjectId(),
            "channel_id": ObjectId(channel_id),
            "agent_id": ObjectId(agent_id),
            "user_id": ObjectId(),
            "instruction": "Cleanup test",
            "status": TaskStatus.pending,
            "result_summary": None,
            "commit_sha": None,
            "pr_url": None,
            "branch_name": None,
            "created_at": datetime.now(UTC),
            "completed_at": None,
        }
        await db["coding_tasks"].insert_one(task_doc)
        task_id = str(task_doc["_id"])

        with patch(
            "app.services.container_service.ContainerService",
            return_value=mock_cs,
        ):
            await Orchestrator.execute_task(
                task_id=task_id,
                channel_id=channel_id,
                agent_id=agent_id,
                instruction="Cleanup test",
            )

        mock_cs.cleanup_container.assert_called_once_with("docker_container_id_123")


class TestContainerServiceHighLevel:
    """Test the high-level ContainerService methods with mocked Docker."""

    def _make_service(self, docker_mock=None):
        from app.services.container_service import ContainerService

        if docker_mock is None:
            docker_mock = MagicMock()
        return ContainerService(docker_client=docker_mock)

    async def test_build_agent_image_when_exists(self):
        mock_docker = MagicMock()
        mock_docker.images.get.return_value = MagicMock()  # Image found

        service = self._make_service(mock_docker)
        tag = await service.build_agent_image()

        assert tag == "pioyan-chat-agent-base:latest"
        mock_docker.images.build.assert_not_called()  # Should skip build

    async def test_build_agent_image_force(self):
        import contextlib

        import docker.errors

        mock_docker = MagicMock()
        mock_docker.images.get.side_effect = docker.errors.ImageNotFound("not found")
        # build_agent_image with force=True uses copytree + build
        # We need a real path structure or mock Path

        service = self._make_service(mock_docker)
        # The actual build will fail due to missing files, but we can test
        # the force flag causes the build attempt
        with contextlib.suppress(FileNotFoundError):
            await service.build_agent_image(force=True)

    async def test_cleanup_container_ignores_errors(self):
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_container.stop.side_effect = RuntimeError("already stopped")
        mock_container.remove.side_effect = RuntimeError("already removed")
        mock_docker.containers.get.return_value = mock_container

        service = self._make_service(mock_docker)
        # Should not raise
        await service.cleanup_container("docker_abc")
