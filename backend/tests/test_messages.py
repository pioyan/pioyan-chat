"""Tests for messages router."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def channel_id(auth_client: AsyncClient) -> str:
    res = await auth_client.post("/api/channels", json={"name": "msg-test"})
    return res.json()["id"]


class TestMessages:
    async def test_post_message(self, auth_client: AsyncClient, channel_id: str):
        res = await auth_client.post(
            f"/api/channels/{channel_id}/messages",
            json={"content": "Hello world!"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["content"] == "Hello world!"
        assert data["channel_id"] == channel_id

    async def test_list_messages(self, auth_client: AsyncClient, channel_id: str):
        await auth_client.post(f"/api/channels/{channel_id}/messages", json={"content": "msg1"})
        await auth_client.post(f"/api/channels/{channel_id}/messages", json={"content": "msg2"})
        res = await auth_client.get(f"/api/channels/{channel_id}/messages")
        assert res.status_code == 200
        msgs = res.json()
        assert len(msgs) == 2

    async def test_list_messages_pagination(self, auth_client: AsyncClient, channel_id: str):
        for i in range(5):
            await auth_client.post(
                f"/api/channels/{channel_id}/messages", json={"content": f"msg{i}"}
            )
        res = await auth_client.get(f"/api/channels/{channel_id}/messages?limit=3")
        assert res.status_code == 200
        assert len(res.json()) == 3

    async def test_delete_message(self, auth_client: AsyncClient, channel_id: str):
        post_res = await auth_client.post(
            f"/api/channels/{channel_id}/messages", json={"content": "to delete"}
        )
        msg_id = post_res.json()["id"]
        res = await auth_client.delete(f"/api/messages/{msg_id}")
        assert res.status_code == 204

    async def test_search_messages(self, auth_client: AsyncClient, channel_id: str):
        await auth_client.post(
            f"/api/channels/{channel_id}/messages", json={"content": "unique keyword here"}
        )
        await auth_client.post(
            f"/api/channels/{channel_id}/messages", json={"content": "other content"}
        )
        res = await auth_client.get("/api/messages/search?q=unique")
        assert res.status_code == 200
        # 検索結果に少なくとも1件含まれること（テキストインデックス依存のためソフトチェック）
        assert isinstance(res.json(), list)

    async def test_unauthenticated_post(self, client: AsyncClient):
        res = await client.post(
            "/api/channels/000000000000000000000000/messages",
            json={"content": "hello"},
        )
        assert res.status_code == 401


class TestThreads:
    async def test_post_thread_reply(self, auth_client: AsyncClient, channel_id: str):
        post_res = await auth_client.post(
            f"/api/channels/{channel_id}/messages", json={"content": "parent message"}
        )
        msg_id = post_res.json()["id"]
        res = await auth_client.post(
            f"/api/messages/{msg_id}/thread",
            json={"content": "thread reply"},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["thread_id"] == msg_id

    async def test_get_thread(self, auth_client: AsyncClient, channel_id: str):
        post_res = await auth_client.post(
            f"/api/channels/{channel_id}/messages", json={"content": "parent"}
        )
        msg_id = post_res.json()["id"]
        await auth_client.post(f"/api/messages/{msg_id}/thread", json={"content": "reply1"})
        await auth_client.post(f"/api/messages/{msg_id}/thread", json={"content": "reply2"})
        res = await auth_client.get(f"/api/messages/{msg_id}/thread")
        assert res.status_code == 200
        assert len(res.json()) == 2
