"""Container management service — Docker operations for agent containers."""

import asyncio
import logging
from pathlib import Path
from typing import Any

import docker
import docker.errors
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Timeout for waiting on container readiness (seconds)
CONTAINER_READY_TIMEOUT = 60
CONTAINER_READY_POLL_INTERVAL = 1.0

# Timeout for task execution (seconds)
TASK_EXECUTION_TIMEOUT = 600  # 10 minutes


class ContainerService:
    """Manages Docker containers for coding agents."""

    CONTAINER_PREFIX = "pioyan-agent"

    def __init__(self, docker_client=None) -> None:
        self._docker = docker_client or docker.from_env()

    # ── Naming helpers ────────────────────────────────────────

    def _container_name(self, agent_id: str, channel_id: str) -> str:
        return f"{self.CONTAINER_PREFIX}-{agent_id}-{channel_id}"

    def _image_name(self, agent_id: str) -> str:
        return f"{self.CONTAINER_PREFIX}-{agent_id}"

    # ── Container lifecycle ───────────────────────────────────

    async def create_container(
        self,
        agent_id: str,
        channel_id: str,
        repo_url: str,
        branch: str,
        github_token: str,
        system_prompt: str | None = None,
    ) -> str:
        """Create a new container for an agent-channel pair.

        Returns the Docker container ID.
        """
        name = self._container_name(agent_id, channel_id)
        env = [
            f"GITHUB_TOKEN={github_token}",
            f"GH_TOKEN={github_token}",
            f"REPO_URL={repo_url}",
            f"BRANCH={branch}",
            f"AGENT_ID={agent_id}",
            f"CHANNEL_ID={channel_id}",
        ]
        if system_prompt:
            env.append(f"SYSTEM_PROMPT={system_prompt}")

        def _create():
            return self._docker.containers.create(
                image=settings.agent_base_image,
                name=name,
                environment=env,
                detach=True,
                network=settings.agent_network,
                ports={"8080/tcp": None},
                # Safety: limit resources
                mem_limit="512m",
                cpu_quota=50000,  # 50% of 1 CPU
            )

        container = await asyncio.to_thread(_create)
        return container.id

    async def start_container(self, container_id: str) -> None:
        """Start an existing container."""

        def _start():
            container = self._docker.containers.get(container_id)
            container.start()

        await asyncio.to_thread(_start)

    async def stop_container(self, container_id: str) -> None:
        """Stop a running container."""

        def _stop():
            container = self._docker.containers.get(container_id)
            container.stop()

        await asyncio.to_thread(_stop)

    async def remove_container(self, container_id: str) -> None:
        """Force-remove a container."""

        def _remove():
            container = self._docker.containers.get(container_id)
            container.remove(force=True)

        await asyncio.to_thread(_remove)

    async def get_container_status(self, container_id: str) -> str | None:
        """Get the status of a container. Returns None if not found."""

        def _status():
            try:
                container = self._docker.containers.get(container_id)
                return container.status
            except docker.errors.NotFound:
                return None

        return await asyncio.to_thread(_status)

    async def execute_in_container(
        self,
        container_id: str,
        command: list[str],
    ) -> dict[str, Any]:
        """Execute a command inside a running container.

        Returns {"exit_code": int, "output": str}.
        """

        def _exec():
            container = self._docker.containers.get(container_id)
            result = container.exec_run(command)
            output = result.output
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace")
            return {"exit_code": result.exit_code, "output": output}

        return await asyncio.to_thread(_exec)

    async def list_agent_containers(self) -> list[dict]:
        """List all pioyan-agent containers."""

        def _list():
            containers = self._docker.containers.list(
                all=True,
                filters={"name": self.CONTAINER_PREFIX},
            )
            return [
                {
                    "id": c.id,
                    "name": c.name,
                    "status": c.status,
                }
                for c in containers
            ]

        return await asyncio.to_thread(_list)

    # ── High-level pipeline helpers ───────────────────────────

    async def build_agent_image(self, force: bool = False) -> str:
        """Build the agent-base Docker image if it doesn't exist.

        Returns the image tag.
        """
        image_tag = settings.agent_base_image

        def _build():
            # Check if image already exists
            if not force:
                try:
                    self._docker.images.get(image_tag)
                    logger.info("Agent base image %s already exists", image_tag)
                    return image_tag
                except docker.errors.ImageNotFound:
                    pass

            dockerfile_dir = Path(__file__).resolve().parents[1] / "container_images" / "agent-base"
            if not dockerfile_dir.exists():
                raise FileNotFoundError(
                    f"Agent base Dockerfile directory not found: {dockerfile_dir}"
                )

            # Copy agent_runtime into build context
            import shutil
            import tempfile

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp = Path(tmpdir)
                # Copy Dockerfile
                shutil.copy2(dockerfile_dir / "Dockerfile", tmp / "Dockerfile")
                # Copy agent_runtime directory
                runtime_src = Path(__file__).resolve().parents[1].parent / "agent_runtime"
                shutil.copytree(runtime_src, tmp / "agent_runtime")

                logger.info("Building agent image %s from %s", image_tag, tmp)
                self._docker.images.build(
                    path=str(tmp),
                    tag=image_tag,
                    rm=True,
                )

            return image_tag

        return await asyncio.to_thread(_build)

    async def _get_host_port(self, container_id: str) -> int:
        """Get the host port mapped to container port 8080."""

        def _inspect():
            container = self._docker.containers.get(container_id)
            container.reload()  # refresh state after start
            ports = container.attrs["NetworkSettings"]["Ports"]
            bindings = ports.get("8080/tcp")
            if not bindings:
                raise RuntimeError(f"No port mapping found for container {container_id[:12]}")
            return int(bindings[0]["HostPort"])

        return await asyncio.to_thread(_inspect)

    async def run_agent_container(
        self,
        agent_id: str,
        channel_id: str,
        repo_url: str,
        branch: str,
        github_token: str,
        system_prompt: str | None = None,
    ) -> tuple[str, str, int]:
        """Build image (if needed), create and start a container.

        Returns (container_id, container_name, host_port).
        """
        await self.build_agent_image()

        container_id = await self.create_container(
            agent_id=agent_id,
            channel_id=channel_id,
            repo_url=repo_url,
            branch=branch,
            github_token=github_token,
            system_prompt=system_prompt,
        )
        await self.start_container(container_id)

        host_port = await self._get_host_port(container_id)
        name = self._container_name(agent_id, channel_id)
        logger.info(
            "Agent container started: %s (id=%s, host_port=%s)",
            name,
            container_id[:12],
            host_port,
        )
        return container_id, name, host_port

    async def wait_for_ready(
        self,
        container_name: str,
        timeout: float = CONTAINER_READY_TIMEOUT,
        host_port: int | None = None,
    ) -> bool:
        """Poll the agent runtime /health endpoint until it responds.

        If *host_port* is provided, poll via ``localhost:{host_port}`` (host→container).
        Otherwise fall back to ``{container_name}:8080`` (container→container).

        Returns True if ready, False if timed out.
        """
        if host_port:
            url = f"http://localhost:{host_port}/health"
        else:
            url = f"http://{container_name}:8080/health"
        elapsed = 0.0

        async with httpx.AsyncClient(timeout=5.0) as http:
            while elapsed < timeout:
                try:
                    resp = await http.get(url)
                    if resp.status_code == 200:
                        logger.info("Agent container %s is ready", container_name)
                        return True
                except (
                    httpx.ConnectError,
                    httpx.TimeoutException,
                    httpx.RemoteProtocolError,
                    httpx.ReadError,
                    OSError,
                ):
                    pass

                await asyncio.sleep(CONTAINER_READY_POLL_INTERVAL)
                elapsed += CONTAINER_READY_POLL_INTERVAL

        logger.warning(
            "Agent container %s did not become ready within %ss",
            container_name,
            timeout,
        )
        return False

    async def send_task(
        self,
        container_name: str,
        task_id: str,
        instruction: str,
        timeout: float = TASK_EXECUTION_TIMEOUT,
        host_port: int | None = None,
    ) -> dict[str, Any]:
        """Send a coding task to the agent runtime inside a container.

        If *host_port* is provided, connect via ``localhost:{host_port}``.
        Otherwise fall back to ``{container_name}:8080``.

        Returns the agent runtime's response dict.
        Raises httpx.HTTPStatusError or httpx.TimeoutException on failure.
        """
        if host_port:
            url = f"http://localhost:{host_port}/task"
        else:
            url = f"http://{container_name}:8080/task"
        payload = {
            "task_id": task_id,
            "instruction": instruction,
            "auto_commit": True,
            "create_pr": True,
        }

        async with httpx.AsyncClient(timeout=timeout) as http:
            resp = await http.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()

    async def cleanup_container(self, container_id: str) -> None:
        """Stop and remove a container, ignoring errors."""
        try:
            await self.stop_container(container_id)
        except Exception:
            logger.debug("Ignoring stop error for container %s", container_id[:12])
        try:
            await self.remove_container(container_id)
        except Exception:
            logger.debug("Ignoring remove error for container %s", container_id[:12])
