"""Tests for container management service (Docker operations mocked)."""

from unittest.mock import MagicMock

from app.services.container_service import ContainerService


class TestContainerService:
    """Tests for ContainerService with mocked Docker client."""

    def _make_service(self, docker_mock=None):
        if docker_mock is None:
            docker_mock = MagicMock()
        return ContainerService(docker_client=docker_mock)

    def test_container_name_format(self):
        service = self._make_service()
        name = service._container_name("agent123", "channel456")
        assert name == "pioyan-agent-agent123-channel456"

    def test_build_agent_image_name(self):
        service = self._make_service()
        name = service._image_name("agent123")
        assert name == "pioyan-agent-agent123"

    async def test_create_container(self):
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_container.id = "docker_container_id_abc"
        mock_container.status = "created"
        mock_docker.containers.create.return_value = mock_container

        service = self._make_service(mock_docker)

        container_id = await service.create_container(
            agent_id="agent1",
            channel_id="ch1",
            repo_url="https://github.com/owner/repo",
            branch="main",
            github_token="ghp_test",
            system_prompt="You are a coder.",
        )

        assert container_id == "docker_container_id_abc"
        mock_docker.containers.create.assert_called_once()
        call_kwargs = mock_docker.containers.create.call_args[1]
        assert call_kwargs["name"] == "pioyan-agent-agent1-ch1"
        assert "GITHUB_TOKEN" in {e.split("=")[0] for e in call_kwargs["environment"]}

    async def test_start_container(self):
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_docker.containers.get.return_value = mock_container

        service = self._make_service(mock_docker)
        await service.start_container("docker_abc")

        mock_docker.containers.get.assert_called_once_with("docker_abc")
        mock_container.start.assert_called_once()

    async def test_stop_container(self):
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_docker.containers.get.return_value = mock_container

        service = self._make_service(mock_docker)
        await service.stop_container("docker_abc")

        mock_container.stop.assert_called_once()

    async def test_remove_container(self):
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_docker.containers.get.return_value = mock_container

        service = self._make_service(mock_docker)
        await service.remove_container("docker_abc")

        mock_container.remove.assert_called_once_with(force=True)

    async def test_get_container_status(self):
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_container.status = "running"
        mock_docker.containers.get.return_value = mock_container

        service = self._make_service(mock_docker)
        status = await service.get_container_status("docker_abc")

        assert status == "running"

    async def test_get_container_status_not_found(self):
        import docker.errors

        mock_docker = MagicMock()
        mock_docker.containers.get.side_effect = docker.errors.NotFound("not found")

        service = self._make_service(mock_docker)
        status = await service.get_container_status("nonexistent")

        assert status is None

    async def test_execute_in_container(self):
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_exec = MagicMock()
        mock_exec.output = b'{"status": "ok", "message": "Done"}'
        mock_exec.exit_code = 0
        mock_container.exec_run.return_value = mock_exec
        mock_docker.containers.get.return_value = mock_container

        service = self._make_service(mock_docker)
        result = await service.execute_in_container(
            "docker_abc",
            command=["python", "run_task.py", "--instruction", "Write a test"],
        )

        assert result["exit_code"] == 0
        assert "Done" in result["output"]

    async def test_execute_in_container_failure(self):
        mock_docker = MagicMock()
        mock_container = MagicMock()
        mock_exec = MagicMock()
        mock_exec.output = b"Error: file not found"
        mock_exec.exit_code = 1
        mock_container.exec_run.return_value = mock_exec
        mock_docker.containers.get.return_value = mock_container

        service = self._make_service(mock_docker)
        result = await service.execute_in_container(
            "docker_abc",
            command=["python", "run_task.py"],
        )

        assert result["exit_code"] == 1
        assert "Error" in result["output"]
