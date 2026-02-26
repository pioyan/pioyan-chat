"""Tests for files router."""

import io

from httpx import AsyncClient


class TestFileUpload:
    async def test_upload_file(self, auth_client: AsyncClient):
        file_content = b"hello file content"
        res = await auth_client.post(
            "/api/files/upload",
            files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")},
        )
        assert res.status_code == 201
        data = res.json()
        assert "file_url" in data
        assert data["filename"] == "test.txt"

    async def test_upload_returns_accessible_url(self, auth_client: AsyncClient):
        file_content = b"image data"
        res = await auth_client.post(
            "/api/files/upload",
            files={"file": ("photo.png", io.BytesIO(file_content), "image/png")},
        )
        assert res.status_code == 201
        url = res.json()["file_url"]
        assert url.startswith("/uploads/")

    async def test_unauthenticated_upload(self, client: AsyncClient):
        res = await client.post(
            "/api/files/upload",
            files={"file": ("test.txt", io.BytesIO(b"data"), "text/plain")},
        )
        assert res.status_code == 401
