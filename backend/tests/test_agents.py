"""Tests for Agent CRUD router and Coding Channel creation."""

from httpx import AsyncClient


class TestAgentRegistration:
    """Tests for POST /api/agents."""

    async def test_create_agent_success(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/agents",
            json={
                "name": "my-coder",
                "description": "A coding agent",
                "system_prompt": "You are a helpful coding assistant.",
            },
        )
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "my-coder"
        assert data["description"] == "A coding agent"
        assert data["system_prompt"] == "You are a helpful coding assistant."
        assert data["source"] == "manual"
        assert data["status"] == "registered"
        assert "id" in data
        assert "owner_id" in data

    async def test_create_agent_minimal(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/agents",
            json={"name": "basic-agent"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "basic-agent"
        assert data["description"] is None
        assert data["system_prompt"] is None

    async def test_create_agent_empty_name_rejected(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/agents",
            json={"name": ""},
        )
        assert res.status_code == 422

    async def test_create_agent_unauthenticated(self, client: AsyncClient):
        res = await client.post(
            "/api/agents",
            json={"name": "agent"},
        )
        assert res.status_code == 401


class TestAgentListAndGet:
    """Tests for GET /api/agents and GET /api/agents/{id}."""

    async def test_list_agents_empty(self, auth_client: AsyncClient):
        res = await auth_client.get("/api/agents")
        assert res.status_code == 200
        assert res.json() == []

    async def test_list_agents_after_creation(self, auth_client: AsyncClient):
        await auth_client.post(
            "/api/agents",
            json={"name": "agent-one"},
        )
        res = await auth_client.get("/api/agents")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["name"] == "agent-one"

    async def test_get_agent_by_id(self, auth_client: AsyncClient):
        create_res = await auth_client.post(
            "/api/agents",
            json={"name": "test-agent", "description": "Test"},
        )
        agent_id = create_res.json()["id"]

        res = await auth_client.get(f"/api/agents/{agent_id}")
        assert res.status_code == 200
        assert res.json()["name"] == "test-agent"

    async def test_get_agent_not_found(self, auth_client: AsyncClient):
        res = await auth_client.get("/api/agents/000000000000000000000000")
        assert res.status_code == 404

    async def test_get_agent_invalid_id(self, auth_client: AsyncClient):
        res = await auth_client.get("/api/agents/not-a-valid-id")
        assert res.status_code == 404


class TestAgentDeletion:
    """Tests for DELETE /api/agents/{id}."""

    async def test_delete_agent(self, auth_client: AsyncClient):
        create_res = await auth_client.post(
            "/api/agents",
            json={"name": "delete-me"},
        )
        agent_id = create_res.json()["id"]

        res = await auth_client.delete(f"/api/agents/{agent_id}")
        assert res.status_code == 204

        # Verify it's gone
        get_res = await auth_client.get(f"/api/agents/{agent_id}")
        assert get_res.status_code == 404

    async def test_delete_agent_not_found(self, auth_client: AsyncClient):
        res = await auth_client.delete("/api/agents/000000000000000000000000")
        assert res.status_code == 404


class TestCodingChannelCreation:
    """Tests for POST /api/channels/coding."""

    async def test_create_coding_channel_success(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/channels/coding",
            json={
                "name": "my-project",
                "repo_url": "https://github.com/owner/repo",
                "description": "A coding project",
            },
        )
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "my-project"
        assert data["is_coding"] is True
        assert data["repo_url"] == "https://github.com/owner/repo"
        assert data["repo_owner"] == "owner"
        assert data["repo_name"] == "repo"
        assert data["default_branch"] == "main"
        assert data["assigned_agents"] == []

    async def test_create_coding_channel_custom_branch(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/channels/coding",
            json={
                "name": "dev-project",
                "repo_url": "https://github.com/org/project",
                "default_branch": "develop",
            },
        )
        assert res.status_code == 201
        assert res.json()["default_branch"] == "develop"

    async def test_create_coding_channel_invalid_url(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/channels/coding",
            json={
                "name": "bad-project",
                "repo_url": "https://gitlab.com/owner/repo",
            },
        )
        assert res.status_code == 422

    async def test_create_coding_channel_unauthenticated(self, client: AsyncClient):
        res = await client.post(
            "/api/channels/coding",
            json={
                "name": "my-project",
                "repo_url": "https://github.com/owner/repo",
            },
        )
        assert res.status_code == 401


class TestChannelAgentAssignment:
    """Tests for agent assignment to coding channels."""

    async def test_assign_agent_to_channel(self, auth_client: AsyncClient):
        # Create agent
        agent_res = await auth_client.post("/api/agents", json={"name": "coder"})
        agent_id = agent_res.json()["id"]

        # Create coding channel
        ch_res = await auth_client.post(
            "/api/channels/coding",
            json={"name": "project", "repo_url": "https://github.com/owner/repo"},
        )
        channel_id = ch_res.json()["id"]

        # Assign
        res = await auth_client.post(f"/api/channels/{channel_id}/agents/{agent_id}")
        assert res.status_code == 200
        data = res.json()
        assert agent_id in data["assigned_agents"]

    async def test_remove_agent_from_channel(self, auth_client: AsyncClient):
        # Create agent and channel
        agent_res = await auth_client.post("/api/agents", json={"name": "coder"})
        agent_id = agent_res.json()["id"]
        ch_res = await auth_client.post(
            "/api/channels/coding",
            json={"name": "project", "repo_url": "https://github.com/owner/repo"},
        )
        channel_id = ch_res.json()["id"]

        # Assign then remove
        await auth_client.post(f"/api/channels/{channel_id}/agents/{agent_id}")
        res = await auth_client.delete(f"/api/channels/{channel_id}/agents/{agent_id}")
        assert res.status_code == 200
        data = res.json()
        assert agent_id not in data["assigned_agents"]

    async def test_list_channel_agents(self, auth_client: AsyncClient):
        # Create 2 agents
        a1 = (await auth_client.post("/api/agents", json={"name": "agent-1"})).json()["id"]
        a2 = (await auth_client.post("/api/agents", json={"name": "agent-2"})).json()["id"]

        # Create coding channel and assign both
        ch_res = await auth_client.post(
            "/api/channels/coding",
            json={"name": "multi-agent", "repo_url": "https://github.com/o/r"},
        )
        channel_id = ch_res.json()["id"]
        await auth_client.post(f"/api/channels/{channel_id}/agents/{a1}")
        await auth_client.post(f"/api/channels/{channel_id}/agents/{a2}")

        # List
        res = await auth_client.get(f"/api/channels/{channel_id}/agents")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 2
        names = {a["name"] for a in data}
        assert names == {"agent-1", "agent-2"}

    async def test_assign_to_non_coding_channel_rejected(self, auth_client: AsyncClient):
        # Create normal channel
        ch_res = await auth_client.post(
            "/api/channels",
            json={"name": "general"},
        )
        channel_id = ch_res.json()["id"]

        # Create agent
        agent_res = await auth_client.post("/api/agents", json={"name": "coder"})
        agent_id = agent_res.json()["id"]

        # Try to assign — should fail for non-coding channel
        res = await auth_client.post(f"/api/channels/{channel_id}/agents/{agent_id}")
        assert res.status_code == 400
