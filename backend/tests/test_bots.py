"""Tests for bots router and container file validation."""

import io

from httpx import AsyncClient


class TestContainerFileValidation:
    """Tests for the /api/bots/validate endpoint."""

    async def test_valid_dockerfile(self, auth_client: AsyncClient):
        dockerfile = (
            b'FROM python:3.13-slim\nRUN pip install copilot-sdk\nCMD ["python", "bot.py"]\n'
        )
        res = await auth_client.post(
            "/api/bots/validate",
            files={"container_file": ("Dockerfile", io.BytesIO(dockerfile), "text/plain")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["valid"] is True
        assert data["errors"] == []

    async def test_empty_file_rejected(self, auth_client: AsyncClient):
        res = await auth_client.post(
            "/api/bots/validate",
            files={"container_file": ("Dockerfile", io.BytesIO(b""), "text/plain")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["valid"] is False
        assert any("empty" in e.lower() for e in data["errors"])

    async def test_missing_from_instruction(self, auth_client: AsyncClient):
        dockerfile = b'RUN echo hello\nCMD ["bash"]\n'
        res = await auth_client.post(
            "/api/bots/validate",
            files={"container_file": ("Dockerfile", io.BytesIO(dockerfile), "text/plain")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["valid"] is False
        assert any("FROM" in e for e in data["errors"])

    async def test_unknown_instruction(self, auth_client: AsyncClient):
        dockerfile = b"FROM ubuntu:22.04\nINVALID something\n"
        res = await auth_client.post(
            "/api/bots/validate",
            files={"container_file": ("Dockerfile", io.BytesIO(dockerfile), "text/plain")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["valid"] is False
        assert any("INVALID" in e for e in data["errors"])

    async def test_unauthenticated_validation(self, client: AsyncClient):
        dockerfile = b"FROM python:3.13-slim\n"
        res = await client.post(
            "/api/bots/validate",
            files={"container_file": ("Dockerfile", io.BytesIO(dockerfile), "text/plain")},
        )
        assert res.status_code == 401


class TestBotRegistration:
    """Tests for the POST /api/bots endpoint."""

    async def test_register_bot_success(self, auth_client: AsyncClient):
        dockerfile = (
            b'FROM python:3.13-slim\nRUN pip install copilot-sdk\nCMD ["python", "bot.py"]\n'
        )
        res = await auth_client.post(
            "/api/bots",
            data={"name": "my-coding-bot", "description": "A test bot"},
            files={"container_file": ("Dockerfile", io.BytesIO(dockerfile), "text/plain")},
        )
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "my-coding-bot"
        assert data["description"] == "A test bot"
        assert data["status"] == "registered"
        assert data["container_file_name"] == "Dockerfile"
        assert "id" in data
        assert "owner_id" in data

    async def test_register_bot_invalid_dockerfile(self, auth_client: AsyncClient):
        dockerfile = b"RUN echo no from\n"
        res = await auth_client.post(
            "/api/bots",
            data={"name": "bad-bot"},
            files={"container_file": ("Dockerfile", io.BytesIO(dockerfile), "text/plain")},
        )
        assert res.status_code == 422

    async def test_register_bot_empty_name(self, auth_client: AsyncClient):
        dockerfile = b"FROM python:3.13-slim\n"
        res = await auth_client.post(
            "/api/bots",
            data={"name": ""},
            files={"container_file": ("Dockerfile", io.BytesIO(dockerfile), "text/plain")},
        )
        assert res.status_code == 422

    async def test_register_bot_unauthenticated(self, client: AsyncClient):
        dockerfile = b"FROM python:3.13-slim\n"
        res = await client.post(
            "/api/bots",
            data={"name": "bot"},
            files={"container_file": ("Dockerfile", io.BytesIO(dockerfile), "text/plain")},
        )
        assert res.status_code == 401

    async def test_register_bot_binary_file_rejected(self, auth_client: AsyncClient):
        binary_content = bytes(range(256))
        res = await auth_client.post(
            "/api/bots",
            data={"name": "binary-bot"},
            files={
                "container_file": (
                    "Dockerfile",
                    io.BytesIO(binary_content),
                    "application/octet-stream",
                )
            },
        )
        assert res.status_code == 422


class TestBotListAndGet:
    """Tests for GET /api/bots and GET /api/bots/{id}."""

    async def test_list_bots_empty(self, auth_client: AsyncClient):
        res = await auth_client.get("/api/bots")
        assert res.status_code == 200
        assert res.json() == []

    async def test_list_bots_after_registration(self, auth_client: AsyncClient):
        dockerfile = b'FROM python:3.13-slim\nCMD ["python"]\n'
        await auth_client.post(
            "/api/bots",
            data={"name": "bot-one"},
            files={"container_file": ("Dockerfile", io.BytesIO(dockerfile), "text/plain")},
        )
        res = await auth_client.get("/api/bots")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["name"] == "bot-one"

    async def test_get_bot_by_id(self, auth_client: AsyncClient):
        dockerfile = b'FROM node:22-slim\nCMD ["node"]\n'
        create_res = await auth_client.post(
            "/api/bots",
            data={"name": "node-bot"},
            files={"container_file": ("Dockerfile", io.BytesIO(dockerfile), "text/plain")},
        )
        bot_id = create_res.json()["id"]

        res = await auth_client.get(f"/api/bots/{bot_id}")
        assert res.status_code == 200
        assert res.json()["name"] == "node-bot"

    async def test_get_bot_not_found(self, auth_client: AsyncClient):
        res = await auth_client.get("/api/bots/000000000000000000000000")
        assert res.status_code == 404


class TestBotDeletion:
    """Tests for DELETE /api/bots/{id}."""

    async def test_delete_bot(self, auth_client: AsyncClient):
        dockerfile = b'FROM python:3.13-slim\nCMD ["python"]\n'
        create_res = await auth_client.post(
            "/api/bots",
            data={"name": "delete-me"},
            files={"container_file": ("Dockerfile", io.BytesIO(dockerfile), "text/plain")},
        )
        bot_id = create_res.json()["id"]

        res = await auth_client.delete(f"/api/bots/{bot_id}")
        assert res.status_code == 204

        # Verify it's gone
        get_res = await auth_client.get(f"/api/bots/{bot_id}")
        assert get_res.status_code == 404

    async def test_delete_bot_not_found(self, auth_client: AsyncClient):
        res = await auth_client.delete("/api/bots/000000000000000000000000")
        assert res.status_code == 404
