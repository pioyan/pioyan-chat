"""Tests for auth router: signup / login / me."""

import io
import os

from httpx import AsyncClient
from PIL import Image

from app.config import settings


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


def _make_jpeg_bytes(size: tuple[int, int] = (400, 400)) -> bytes:
    img = Image.new("RGB", size, color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestUploadAvatar:
    async def test_upload_avatar_success(self, auth_client: AsyncClient):
        jpeg_bytes = _make_jpeg_bytes()
        res = await auth_client.post(
            "/api/auth/me/avatar",
            files={"file": ("avatar.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["avatar_url"] is not None
        assert data["avatar_url"].startswith("/uploads/avatar_")
        assert data["avatar_url"].endswith(".jpg")

    async def test_upload_avatar_resizes_image(self, auth_client: AsyncClient):
        """アップロードされた画像が 256×256 以下にリサイズされること"""
        jpeg_bytes = _make_jpeg_bytes((800, 600))
        res = await auth_client.post(
            "/api/auth/me/avatar",
            files={"file": ("large.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        )
        assert res.status_code == 200
        avatar_url = res.json()["avatar_url"]
        stored_name = avatar_url.removeprefix("/uploads/")
        saved_path = os.path.join(settings.upload_dir, stored_name)
        with Image.open(saved_path) as img:
            assert img.width <= 256
            assert img.height <= 256

    async def test_upload_avatar_unsupported_type(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/auth/me/avatar",
            files={"file": ("doc.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
        )
        assert res.status_code == 415

    async def test_upload_avatar_invalid_image(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/auth/me/avatar",
            files={"file": ("broken.jpg", io.BytesIO(b"not an image"), "image/jpeg")},
        )
        assert res.status_code == 400

    async def test_upload_avatar_unauthenticated(self, client: AsyncClient):
        jpeg_bytes = _make_jpeg_bytes()
        res = await client.post(
            "/api/auth/me/avatar",
            files={"file": ("avatar.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
        )
        assert res.status_code == 401
