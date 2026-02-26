"""Tests for auth router: signup / login / me."""

from httpx import AsyncClient


class TestSignup:
    async def test_signup_success(self, client: AsyncClient):
        res = await client.post(
            "/api/auth/signup",
            json={
                "username": "alice",
                "email": "alice@example.com",
                "password": "securepass",
            },
        )
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_signup_duplicate_email(self, client: AsyncClient):
        payload = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "securepass",
        }
        await client.post("/api/auth/signup", json=payload)
        res = await client.post("/api/auth/signup", json=payload)
        assert res.status_code == 409

    async def test_signup_duplicate_username(self, client: AsyncClient):
        await client.post(
            "/api/auth/signup",
            json={"username": "alice", "email": "alice@example.com", "password": "pass1234"},
        )
        res = await client.post(
            "/api/auth/signup",
            json={"username": "alice", "email": "other@example.com", "password": "pass1234"},
        )
        assert res.status_code == 409

    async def test_signup_invalid_data(self, client: AsyncClient):
        res = await client.post(
            "/api/auth/signup",
            json={"username": "a", "email": "bad", "password": "123"},
        )
        assert res.status_code == 422


class TestLogin:
    async def test_login_success(self, client: AsyncClient):
        await client.post(
            "/api/auth/signup",
            json={
                "username": "bob",
                "email": "bob@example.com",
                "password": "securepass",
            },
        )
        res = await client.post(
            "/api/auth/login",
            json={"email": "bob@example.com", "password": "securepass"},
        )
        assert res.status_code == 200
        assert "access_token" in res.json()

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post(
            "/api/auth/signup",
            json={"username": "bob", "email": "bob@example.com", "password": "securepass"},
        )
        res = await client.post(
            "/api/auth/login",
            json={"email": "bob@example.com", "password": "wrongpass"},
        )
        assert res.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        res = await client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "pass1234"},
        )
        assert res.status_code == 401


class TestMe:
    async def test_me_authenticated(self, auth_client: AsyncClient):
        res = await auth_client.get("/api/auth/me")
        assert res.status_code == 200
        data = res.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data

    async def test_me_unauthenticated(self, client: AsyncClient):
        res = await client.get("/api/auth/me")
        assert res.status_code == 401
