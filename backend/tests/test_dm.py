"""Tests for DM router."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def bob_id(client: AsyncClient) -> str:
    """Create bob user and return his ID."""
    res = await client.post(
        "/api/auth/signup",
        json={"username": "bob", "email": "bob@example.com", "password": "pass1234"},
    )
    token = res.json()["access_token"]
    bob_client = AsyncClient(
        transport=client._transport,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    )
    async with bob_client:
        me_res = await bob_client.get("/api/auth/me")
        return me_res.json()["id"]


class TestDM:
    async def test_start_dm(self, auth_client: AsyncClient, bob_id: str):
        res = await auth_client.post("/api/dm", json={"user_id": bob_id})
        assert res.status_code == 201
        data = res.json()
        assert data["is_private"] is True
        assert bob_id in data["members"]

    async def test_start_dm_idempotent(self, auth_client: AsyncClient, bob_id: str):
        res1 = await auth_client.post("/api/dm", json={"user_id": bob_id})
        res2 = await auth_client.post("/api/dm", json={"user_id": bob_id})
        assert res1.json()["id"] == res2.json()["id"]

    async def test_list_dms(self, auth_client: AsyncClient, bob_id: str):
        await auth_client.post("/api/dm", json={"user_id": bob_id})
        res = await auth_client.get("/api/dm")
        assert res.status_code == 200
        dms = res.json()
        assert len(dms) >= 1

    async def test_dm_messages(self, auth_client: AsyncClient, bob_id: str):
        dm_res = await auth_client.post("/api/dm", json={"user_id": bob_id})
        conv_id = dm_res.json()["id"]
        await auth_client.post(
            f"/api/channels/{conv_id}/messages",
            json={"content": "Hi Bob!"},
        )
        res = await auth_client.get(f"/api/dm/{conv_id}/messages")
        assert res.status_code == 200
        msgs = res.json()
        assert len(msgs) == 1
        assert msgs[0]["content"] == "Hi Bob!"

    async def test_unauthenticated(self, client: AsyncClient):
        res = await client.post("/api/dm", json={"user_id": "anyid"})
        assert res.status_code == 401
