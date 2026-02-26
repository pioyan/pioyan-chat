"""Tests for channels router."""

from httpx import AsyncClient


class TestChannelCRUD:
    async def test_create_channel(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/channels",
            json={"name": "general", "description": "General discussion"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "general"
        assert "id" in data
        assert "testuser" in data["members"] or len(data["members"]) > 0

    async def test_list_channels(self, auth_client: AsyncClient):
        await auth_client.post("/api/channels", json={"name": "ch1"})
        await auth_client.post("/api/channels", json={"name": "ch2"})
        res = await auth_client.get("/api/channels")
        assert res.status_code == 200
        channels = res.json()
        assert len(channels) >= 2

    async def test_get_channel(self, auth_client: AsyncClient):
        create_res = await auth_client.post("/api/channels", json={"name": "alpha"})
        channel_id = create_res.json()["id"]
        res = await auth_client.get(f"/api/channels/{channel_id}")
        assert res.status_code == 200
        assert res.json()["name"] == "alpha"

    async def test_get_channel_not_found(self, auth_client: AsyncClient):
        res = await auth_client.get("/api/channels/000000000000000000000000")
        assert res.status_code == 404

    async def test_update_channel(self, auth_client: AsyncClient):
        create_res = await auth_client.post("/api/channels", json={"name": "old-name"})
        channel_id = create_res.json()["id"]
        res = await auth_client.put(
            f"/api/channels/{channel_id}",
            json={"name": "new-name", "description": "Updated"},
        )
        assert res.status_code == 200
        assert res.json()["name"] == "new-name"

    async def test_delete_channel(self, auth_client: AsyncClient):
        create_res = await auth_client.post("/api/channels", json={"name": "to-delete"})
        channel_id = create_res.json()["id"]
        res = await auth_client.delete(f"/api/channels/{channel_id}")
        assert res.status_code == 204
        get_res = await auth_client.get(f"/api/channels/{channel_id}")
        assert get_res.status_code == 404

    async def test_unauthenticated_create(self, client: AsyncClient):
        res = await client.post("/api/channels", json={"name": "test"})
        assert res.status_code == 401


class TestChannelMembers:
    async def test_add_member(self, auth_client: AsyncClient, client: AsyncClient):
        # 2人目のユーザーを作成
        signup_res = await client.post(
            "/api/auth/signup",
            json={"username": "bob", "email": "bob@example.com", "password": "pass1234"},
        )
        bob_token = signup_res.json()["access_token"]
        # bobのIDを取得
        bob_client = AsyncClient(
            transport=auth_client._transport,
            base_url="http://test",
            headers={"Authorization": f"Bearer {bob_token}"},
        )
        async with bob_client:
            me_res = await bob_client.get("/api/auth/me")
            bob_id = me_res.json()["id"]

        # チャンネル作成
        ch_res = await auth_client.post("/api/channels", json={"name": "team"})
        channel_id = ch_res.json()["id"]
        # メンバー追加
        res = await auth_client.post(
            f"/api/channels/{channel_id}/members",
            json={"user_id": bob_id},
        )
        assert res.status_code == 200
        assert bob_id in res.json()["members"]

    async def test_remove_member(self, auth_client: AsyncClient, client: AsyncClient):
        signup_res = await client.post(
            "/api/auth/signup",
            json={"username": "carol", "email": "carol@example.com", "password": "pass1234"},
        )
        carol_token = signup_res.json()["access_token"]
        carol_client = AsyncClient(
            transport=auth_client._transport,
            base_url="http://test",
            headers={"Authorization": f"Bearer {carol_token}"},
        )
        async with carol_client:
            me_res = await carol_client.get("/api/auth/me")
            carol_id = me_res.json()["id"]

        ch_res = await auth_client.post("/api/channels", json={"name": "remove-test"})
        channel_id = ch_res.json()["id"]
        await auth_client.post(f"/api/channels/{channel_id}/members", json={"user_id": carol_id})
        res = await auth_client.delete(f"/api/channels/{channel_id}/members/{carol_id}")
        assert res.status_code == 200
        assert carol_id not in res.json()["members"]
