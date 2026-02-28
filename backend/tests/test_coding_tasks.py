"""Tests for Coding Tasks router — submit and track coding instructions."""

from httpx import AsyncClient


async def _create_coding_channel_with_agent(auth_client: AsyncClient):
    """Helper: create a coding channel and assign an agent. Returns (channel_id, agent_id, agent_name)."""
    agent_res = await auth_client.post(
        "/api/agents",
        json={"name": "code-bot", "system_prompt": "You code."},
    )
    agent_id = agent_res.json()["id"]

    ch_res = await auth_client.post(
        "/api/channels/coding",
        json={"name": "project-x", "repo_url": "https://github.com/owner/repo"},
    )
    channel_id = ch_res.json()["id"]

    await auth_client.post(f"/api/channels/{channel_id}/agents/{agent_id}")
    return channel_id, agent_id, "code-bot"


class TestCreateCodingTask:
    """Tests for POST /api/channels/{channel_id}/tasks."""

    async def test_create_task_with_explicit_agent(self, auth_client: AsyncClient):
        channel_id, agent_id, _ = await _create_coding_channel_with_agent(auth_client)

        res = await auth_client.post(
            f"/api/channels/{channel_id}/tasks",
            json={"instruction": "Fix the login bug", "agent_id": agent_id},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["instruction"] == "Fix the login bug"
        assert data["agent_id"] == agent_id
        assert data["channel_id"] == channel_id
        assert data["status"] == "pending"
        assert "id" in data
        assert "user_id" in data
        assert data["result_summary"] is None
        assert data["commit_sha"] is None
        assert data["pr_url"] is None

    async def test_create_task_with_mention_routing(self, auth_client: AsyncClient):
        channel_id, agent_id, _ = await _create_coding_channel_with_agent(auth_client)

        res = await auth_client.post(
            f"/api/channels/{channel_id}/tasks",
            json={"instruction": "@code-bot implement auth module"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["agent_id"] == agent_id
        # Instruction should have mention cleaned
        assert data["instruction"] == "implement auth module"

    async def test_create_task_orchestrator_fallback(self, auth_client: AsyncClient):
        channel_id, agent_id, _ = await _create_coding_channel_with_agent(auth_client)

        res = await auth_client.post(
            f"/api/channels/{channel_id}/tasks",
            json={"instruction": "Refactor the database layer"},
        )
        assert res.status_code == 201
        data = res.json()
        # Orchestrator should pick the only available agent
        assert data["agent_id"] == agent_id
        assert data["instruction"] == "Refactor the database layer"

    async def test_create_task_non_coding_channel_rejected(self, auth_client: AsyncClient):
        # Create normal channel
        ch_res = await auth_client.post(
            "/api/channels",
            json={"name": "general"},
        )
        channel_id = ch_res.json()["id"]

        res = await auth_client.post(
            f"/api/channels/{channel_id}/tasks",
            json={"instruction": "Do something"},
        )
        assert res.status_code == 400
        assert "Not a coding channel" in res.json()["detail"]

    async def test_create_task_channel_not_found(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/channels/000000000000000000000000/tasks",
            json={"instruction": "Do something"},
        )
        assert res.status_code == 404

    async def test_create_task_no_agents_available(self, auth_client: AsyncClient):
        # Create coding channel without assigning any agents
        ch_res = await auth_client.post(
            "/api/channels/coding",
            json={"name": "empty-project", "repo_url": "https://github.com/o/r"},
        )
        channel_id = ch_res.json()["id"]

        res = await auth_client.post(
            f"/api/channels/{channel_id}/tasks",
            json={"instruction": "Help me code"},
        )
        assert res.status_code == 400
        assert "No agents available" in res.json()["detail"]

    async def test_create_task_unauthenticated(self, client: AsyncClient):
        res = await client.post(
            "/api/channels/000000000000000000000000/tasks",
            json={"instruction": "Do something"},
        )
        assert res.status_code == 401


class TestListCodingTasks:
    """Tests for GET /api/channels/{channel_id}/tasks."""

    async def test_list_tasks_empty(self, auth_client: AsyncClient):
        channel_id, _, _ = await _create_coding_channel_with_agent(auth_client)

        res = await auth_client.get(f"/api/channels/{channel_id}/tasks")
        assert res.status_code == 200
        assert res.json() == []

    async def test_list_tasks_returns_created(self, auth_client: AsyncClient):
        channel_id, agent_id, _ = await _create_coding_channel_with_agent(auth_client)

        await auth_client.post(
            f"/api/channels/{channel_id}/tasks",
            json={"instruction": "Task one", "agent_id": agent_id},
        )
        await auth_client.post(
            f"/api/channels/{channel_id}/tasks",
            json={"instruction": "Task two", "agent_id": agent_id},
        )

        res = await auth_client.get(f"/api/channels/{channel_id}/tasks")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 2
        # Sorted by created_at desc — newest first
        assert data[0]["instruction"] == "Task two"
        assert data[1]["instruction"] == "Task one"

    async def test_list_tasks_only_for_channel(self, auth_client: AsyncClient):
        """Tasks from one channel should not appear in another's list."""
        ch1, a1, _ = await _create_coding_channel_with_agent(auth_client)

        # Create second coding channel
        ch2_res = await auth_client.post(
            "/api/channels/coding",
            json={"name": "project-y", "repo_url": "https://github.com/o/r2"},
        )
        ch2 = ch2_res.json()["id"]
        # Assign same agent to ch2
        await auth_client.post(f"/api/channels/{ch2}/agents/{a1}")

        # Create task in ch1 only
        await auth_client.post(
            f"/api/channels/{ch1}/tasks",
            json={"instruction": "Only in ch1", "agent_id": a1},
        )

        res = await auth_client.get(f"/api/channels/{ch2}/tasks")
        assert res.status_code == 200
        assert res.json() == []


class TestGetCodingTask:
    """Tests for GET /api/channels/{channel_id}/tasks/{task_id}."""

    async def test_get_task_by_id(self, auth_client: AsyncClient):
        channel_id, agent_id, _ = await _create_coding_channel_with_agent(auth_client)

        create_res = await auth_client.post(
            f"/api/channels/{channel_id}/tasks",
            json={"instruction": "Build feature X", "agent_id": agent_id},
        )
        task_id = create_res.json()["id"]

        res = await auth_client.get(f"/api/channels/{channel_id}/tasks/{task_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == task_id
        assert data["instruction"] == "Build feature X"
        assert data["channel_id"] == channel_id

    async def test_get_task_not_found(self, auth_client: AsyncClient):
        channel_id, _, _ = await _create_coding_channel_with_agent(auth_client)

        res = await auth_client.get(f"/api/channels/{channel_id}/tasks/000000000000000000000000")
        assert res.status_code == 404

    async def test_get_task_wrong_channel(self, auth_client: AsyncClient):
        """Task should not be accessible from a different channel."""
        ch1, a1, _ = await _create_coding_channel_with_agent(auth_client)

        create_res = await auth_client.post(
            f"/api/channels/{ch1}/tasks",
            json={"instruction": "Specific task", "agent_id": a1},
        )
        task_id = create_res.json()["id"]

        # Create another coding channel
        ch2_res = await auth_client.post(
            "/api/channels/coding",
            json={"name": "other-project", "repo_url": "https://github.com/o/r3"},
        )
        ch2 = ch2_res.json()["id"]

        # Try to access task via wrong channel
        res = await auth_client.get(f"/api/channels/{ch2}/tasks/{task_id}")
        assert res.status_code == 404
