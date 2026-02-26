"""Shared pytest fixtures for pioyan-chat backend tests."""

import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# テスト用DB名を設定（本番DBと分離）
os.environ.setdefault(
    "MONGO_URL",
    "mongodb://admin:password@localhost:27017/pioyan_chat_test?authSource=admin",
)
os.environ.setdefault("MONGO_DB", "pioyan_chat_test")


@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient fixture pointing at the FastAPI app."""
    from app.database import close_connection, get_db
    from app.main import app

    db = get_db()
    # テスト前にDBをクリア
    for col in await db.list_collection_names():
        await db[col].drop()

    # テキストインデックスを作成（テストDB用）
    await db["messages"].create_index([("content", "text")])
    await db["messages"].create_index("channel_id")
    await db["channels"].create_index("name")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # テスト後にDBをクリア
    for col in await db.list_collection_names():
        await db[col].drop()
    await close_connection()


@pytest_asyncio.fixture(scope="function")
async def auth_client(client: AsyncClient):
    """ログイン済みの AsyncClient を返す fixture。"""
    # テストユーザー作成
    res = await client.post(
        "/api/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert res.status_code == 201, res.text
    token = res.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
