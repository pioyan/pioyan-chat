"""Error resilience tests for the coding task pipeline (Phase D-3).

Tests error scenarios: invalid repository URLs, Docker failures,
invalid tokens, timeouts, and unexpected container exits.

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
        json={"name": "resilience-bot", "system_prompt": "You build apps."},
    )
    agent_id = agent_res.json()["id"]

    ch_res = await auth_client.post(
        "/api/channels/coding",
        json={
            "name": "resilience-test",
            "repo_url": "https://github.com/pioyan/talent-flow",
        },
    )
    channel_id = ch_res.json()["id"]

    await auth_client.post(f"/api/channels/{channel_id}/agents/{agent_id}")
    return channel_id, agent_id


def _mock_container_service(**overrides):
    """Return a mock ContainerService with sensible defaults.

    Pass keyword args to override specific AsyncMock return values / side effects.
    """
    mock = MagicMock()
    mock.build_agent_image = AsyncMock(return_value="pioyan-chat-agent-base:latest")
    mock.create_container = AsyncMock(return_value="docker_container_id_999")
    mock.start_container = AsyncMock()
    mock.run_agent_container = AsyncMock(
        return_value=("docker_container_id_999", "pioyan-agent-a1-ch1", 32768),
    )
    mock.wait_for_ready = AsyncMock(return_value=True)
    mock.send_task = AsyncMock(
        return_value={
            "status": "completed",
            "task_id": "placeholder",
            "response": "Generated code",
            "summary": "Completed task",
            "files_modified": [],
            "commit_sha": "abc123",
            "pr_url": "https://github.com/pioyan/talent-flow/pull/99",
            "branch_name": "agent/resilience-bot/abc123",
        },
    )
    mock.cleanup_container = AsyncMock()
    mock.stop_container = AsyncMock()
    mock.remove_container = AsyncMock()

    for key, val in overrides.items():
        setattr(mock, key, val)
    return mock


async def _create_task(db, channel_id: str, agent_id: str, instruction: str) -> str:
    """Insert a pending task into DB and return its string ID."""
    doc = {
        "_id": ObjectId(),
        "channel_id": ObjectId(channel_id),
        "agent_id": ObjectId(agent_id),
        "user_id": ObjectId(),
        "instruction": instruction,
        "status": TaskStatus.pending,
        "result_summary": None,
        "commit_sha": None,
        "pr_url": None,
        "branch_name": None,
        "created_at": datetime.now(UTC),
        "completed_at": None,
    }
    await db["coding_tasks"].insert_one(doc)
    return str(doc["_id"])


async def _run_task(mock_cs, task_id, channel_id, agent_id, instruction):
    """Execute a task via Orchestrator with a mocked ContainerService."""
    from app.services.orchestrator import Orchestrator

    with patch(
        "app.services.container_service.ContainerService",
        return_value=mock_cs,
    ):
        await Orchestrator.execute_task(
            task_id=task_id,
            channel_id=channel_id,
            agent_id=agent_id,
            instruction=instruction,
        )


async def _get_task(db, task_id: str) -> dict:
    """Fetch a task document by string ID."""
    return await db["coding_tasks"].find_one({"_id": ObjectId(task_id)})


# ── 1. Invalid Repository URL ────────────────────────────────


class TestInvalidRepoUrl:
    """Tasks with invalid repo_url should fail gracefully."""

    async def test_empty_repo_url(self, auth_client: AsyncClient):
        """Empty repo_url → immediate failure without container ops."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()

        # Clear the repo URL
        await db["channels"].update_one(
            {"_id": ObjectId(channel_id)},
            {"$set": {"repo_url": ""}},
        )

        task_id = await _create_task(db, channel_id, agent_id, "Build login page")
        mock_cs = _mock_container_service()

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Build login page")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        assert "repo_url" in task["result_summary"].lower()
        mock_cs.run_agent_container.assert_not_called()

    async def test_none_repo_url(self, auth_client: AsyncClient):
        """None repo_url → immediate failure."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()

        await db["channels"].update_one(
            {"_id": ObjectId(channel_id)},
            {"$set": {"repo_url": None}},
        )

        task_id = await _create_task(db, channel_id, agent_id, "Add tests")
        mock_cs = _mock_container_service()

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Add tests")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        mock_cs.run_agent_container.assert_not_called()

    async def test_nonexistent_channel(self, auth_client: AsyncClient):
        """Task referencing a deleted channel → immediate failure."""
        from app.database import get_db

        _, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        fake_channel_id = str(ObjectId())

        task_id = await _create_task(db, fake_channel_id, agent_id, "Do something")
        mock_cs = _mock_container_service()

        await _run_task(mock_cs, task_id, fake_channel_id, agent_id, "Do something")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        assert "not found" in task["result_summary"].lower()
        mock_cs.run_agent_container.assert_not_called()


# ── 2. Docker Daemon Failures ────────────────────────────────


class TestDockerFailures:
    """Docker daemon and container management errors."""

    async def test_docker_daemon_not_running(self, auth_client: AsyncClient):
        """Docker daemon unreachable → task failed with clear error."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Build feature")

        mock_cs = _mock_container_service(
            run_agent_container=AsyncMock(
                side_effect=ConnectionError("Cannot connect to Docker daemon"),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Build feature")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        assert "docker" in task["result_summary"].lower() or "connect" in task["result_summary"].lower()
        assert task["completed_at"] is not None

    async def test_docker_image_not_found(self, auth_client: AsyncClient):
        """Agent base image missing → task failed."""
        import docker.errors

        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Build dashboard")

        mock_cs = _mock_container_service(
            run_agent_container=AsyncMock(
                side_effect=docker.errors.ImageNotFound(
                    "Image pioyan-chat-agent-base:latest not found",
                ),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Build dashboard")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        assert "image" in task["result_summary"].lower() or "not found" in task["result_summary"].lower()

    async def test_docker_api_error(self, auth_client: AsyncClient):
        """Docker API returns a server error → task failed."""
        import docker.errors

        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Run analysis")

        mock_cs = _mock_container_service(
            run_agent_container=AsyncMock(
                side_effect=docker.errors.APIError("Server error"),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Run analysis")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        assert task["completed_at"] is not None

    async def test_container_exits_during_readiness_check(self, auth_client: AsyncClient):
        """Container crashes during startup → wait_for_ready returns False → task failed."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Build auth")

        mock_cs = _mock_container_service(
            wait_for_ready=AsyncMock(return_value=False),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Build auth")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        assert "timeout" in task["result_summary"].lower() or "ready" in task["result_summary"].lower()
        mock_cs.cleanup_container.assert_called_once()

    async def test_cleanup_error_does_not_propagate(self, auth_client: AsyncClient):
        """Even if cleanup fails, the task status is still correctly updated."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Complete task")

        mock_cs = _mock_container_service(
            cleanup_container=AsyncMock(
                side_effect=RuntimeError("Container already removed"),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Complete task")

        task = await _get_task(db, task_id)
        # Task should complete successfully despite cleanup failure
        assert task["status"] == TaskStatus.completed
        assert task["completed_at"] is not None


# ── 3. Invalid / Expired Token ───────────────────────────────


class TestInvalidToken:
    """GitHub token authentication failures."""

    async def test_git_clone_auth_failure(self, auth_client: AsyncClient):
        """Agent runtime fails due to git clone authentication error → task failed."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Build feature X")

        mock_cs = _mock_container_service(
            send_task=AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Authentication failed: git clone returned exit code 128",
                    request=httpx.Request("POST", "http://localhost:32768/task"),
                    response=httpx.Response(500, json={
                        "error": "git clone failed: Authentication failed for https://github.com/..."
                    }),
                ),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Build feature X")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        assert "error" in task["result_summary"].lower()
        mock_cs.cleanup_container.assert_called_once()

    async def test_pr_creation_auth_failure(self, auth_client: AsyncClient):
        """Agent runtime sends 500 because gh pr create fails (bad token) → task failed."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Add CI config")

        mock_cs = _mock_container_service(
            send_task=AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "PR creation failed: HTTP 401, message: Bad credentials",
                    request=httpx.Request("POST", "http://localhost:32768/task"),
                    response=httpx.Response(500, json={
                        "error": "gh pr create: HTTP 401, message: Bad credentials"
                    }),
                ),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Add CI config")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        mock_cs.cleanup_container.assert_called_once()


# ── 4. Timeout Scenarios ─────────────────────────────────────


class TestTimeoutScenarios:
    """Various timeout conditions during pipeline execution."""

    async def test_task_execution_timeout(self, auth_client: AsyncClient):
        """Agent runtime takes too long → httpx.TimeoutException → task failed."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Complex refactor")

        mock_cs = _mock_container_service(
            send_task=AsyncMock(
                side_effect=httpx.TimeoutException(
                    "Timed out after 600s waiting for response",
                ),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Complex refactor")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        assert "timeout" in task["result_summary"].lower() or "timed out" in task["result_summary"].lower()
        mock_cs.cleanup_container.assert_called_once()

    async def test_health_check_timeout(self, auth_client: AsyncClient):
        """Agent runtime never responds to health check → timeout → task failed."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Quick task")

        mock_cs = _mock_container_service(
            wait_for_ready=AsyncMock(return_value=False),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Quick task")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        assert "timeout" in task["result_summary"].lower() or "ready" in task["result_summary"].lower()
        # Container registration and cleanup still happen
        mock_cs.run_agent_container.assert_called_once()
        mock_cs.cleanup_container.assert_called_once()


# ── 5. Network Errors ────────────────────────────────────────


class TestNetworkErrors:
    """Network connectivity issues during pipeline execution."""

    async def test_connection_refused_during_task(self, auth_client: AsyncClient):
        """Agent runtime port is bound but connection refused → task failed."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Build module")

        mock_cs = _mock_container_service(
            send_task=AsyncMock(
                side_effect=httpx.ConnectError("Connection refused"),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Build module")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        mock_cs.cleanup_container.assert_called_once()

    async def test_remote_protocol_error_during_task(self, auth_client: AsyncClient):
        """Server disconnects mid-response → task failed."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Run migration")

        mock_cs = _mock_container_service(
            send_task=AsyncMock(
                side_effect=httpx.RemoteProtocolError(
                    "Server disconnected without sending a response",
                ),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Run migration")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        mock_cs.cleanup_container.assert_called_once()

    async def test_read_error_during_task(self, auth_client: AsyncClient):
        """Network read error during task response → task failed."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Generate docs")

        mock_cs = _mock_container_service(
            send_task=AsyncMock(
                side_effect=httpx.ReadError("Connection reset by peer"),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Generate docs")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        mock_cs.cleanup_container.assert_called_once()


# ── 6. Concurrent & Edge Cases ───────────────────────────────


class TestEdgeCases:
    """Edge cases and concurrent execution scenarios."""

    async def test_agent_not_found_still_proceeds(self, auth_client: AsyncClient):
        """If the agent is deleted before execution, system_prompt is None but task runs."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()

        # Delete the agent from DB
        await db["agents"].delete_one({"_id": ObjectId(agent_id)})

        task_id = await _create_task(db, channel_id, agent_id, "Build feature")
        mock_cs = _mock_container_service()

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Build feature")

        task = await _get_task(db, task_id)
        # Should still complete — missing agent just means no system_prompt
        assert task["status"] == TaskStatus.completed

    async def test_empty_instruction(self, auth_client: AsyncClient):
        """Empty instruction is passed to agent as-is (agent decides what to do)."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "")
        mock_cs = _mock_container_service()

        await _run_task(mock_cs, task_id, channel_id, agent_id, "")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.completed
        mock_cs.send_task.assert_called_once()

    async def test_multiple_exceptions_in_pipeline(self, auth_client: AsyncClient):
        """Both task execution and cleanup fail → task still fails gracefully."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Doomed task")

        mock_cs = _mock_container_service(
            send_task=AsyncMock(
                side_effect=RuntimeError("Agent crash"),
            ),
            cleanup_container=AsyncMock(
                side_effect=RuntimeError("Container already gone"),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Doomed task")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        assert task["completed_at"] is not None

    async def test_port_mapping_failure(self, auth_client: AsyncClient):
        """Port mapping retrieval fails → task failed with error."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Setup CI")

        mock_cs = _mock_container_service(
            run_agent_container=AsyncMock(
                side_effect=RuntimeError("No port mapping found for container"),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Setup CI")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        assert "port" in task["result_summary"].lower() or "mapping" in task["result_summary"].lower()

    async def test_http_422_from_agent_runtime(self, auth_client: AsyncClient):
        """Agent runtime returns 422 (bad request) → task failed."""
        from app.database import get_db

        channel_id, agent_id = await _setup_coding_channel_with_agent(auth_client)
        db = get_db()
        task_id = await _create_task(db, channel_id, agent_id, "Invalid instruction")

        mock_cs = _mock_container_service(
            send_task=AsyncMock(
                side_effect=httpx.HTTPStatusError(
                    "Unprocessable Entity",
                    request=httpx.Request("POST", "http://localhost:32768/task"),
                    response=httpx.Response(422, json={"detail": "Invalid task format"}),
                ),
            ),
        )

        await _run_task(mock_cs, task_id, channel_id, agent_id, "Invalid instruction")

        task = await _get_task(db, task_id)
        assert task["status"] == TaskStatus.failed
        mock_cs.cleanup_container.assert_called_once()
