"""Orchestrator service — routes messages to appropriate agents and executes tasks."""

import logging
from datetime import UTC, datetime
from typing import Any

from app.services.mention_parser import MentionParser

logger = logging.getLogger(__name__)


class Orchestrator:
    """Routes coding instructions to appropriate agents and executes tasks.

    When a user sends a message in a coding channel:
    1. Parse @mentions → route to specific agent(s)
    2. No mention → orchestrator analyzes and delegates

    After routing, execute_task() handles the full pipeline:
    container startup → task submission → result collection → DB update.
    """

    @staticmethod
    async def route_instruction(
        message: str,
        available_agents: dict[str, str],
    ) -> dict[str, Any]:
        """Determine which agent(s) should handle an instruction.

        Args:
            message: The raw message text (may contain @mentions).
            available_agents: {agent_id: agent_name} mapping of
                agents assigned to the channel.

        Returns:
            {
                "target_agent_ids": list[str],
                "instruction": str,  # cleaned instruction
                "is_orchestrated": bool,  # True if orchestrator chose
            }
        """
        result = MentionParser.parse(message)

        # If mentions found, match against available agents
        matched_ids = result.match_agents(available_agents)

        if matched_ids:
            return {
                "target_agent_ids": matched_ids,
                "instruction": result.clean_text,
                "is_orchestrated": False,
            }

        # No mention — delegate to orchestrator logic
        # For now: pick the first available agent
        # In future: use Copilot SDK to analyze intent and pick best agent
        if available_agents:
            first_agent_id = next(iter(available_agents))
            logger.info(
                "No mention found, orchestrator delegating to agent %s",
                first_agent_id,
            )
            return {
                "target_agent_ids": [first_agent_id],
                "instruction": result.clean_text,
                "is_orchestrated": True,
            }

        return {
            "target_agent_ids": [],
            "instruction": result.clean_text,
            "is_orchestrated": True,
        }

    @staticmethod
    async def execute_task(
        task_id: str,
        channel_id: str,
        agent_id: str,
        instruction: str,
    ) -> None:
        """Execute a coding task end-to-end: container → agent runtime → DB update.

        This method is designed to run as a FastAPI BackgroundTask.
        It handles its own error handling and always updates the task status.
        """
        from bson import ObjectId

        from app.config import settings
        from app.database import get_db
        from app.models.coding_task import TaskStatus
        from app.services.container_service import ContainerService
        from app.sockets import emit_task_status

        db = get_db()
        task_oid = ObjectId(task_id)
        container_id: str | None = None
        host_port: int | None = None
        container_service = ContainerService()

        async def _update_task(status: TaskStatus, **fields: Any) -> None:
            """Helper to update task status in DB and notify via Socket.IO."""
            update_doc: dict[str, Any] = {"status": status, **fields}
            if status in (TaskStatus.completed, TaskStatus.failed):
                update_doc["completed_at"] = datetime.now(UTC)
            await db["coding_tasks"].update_one(
                {"_id": task_oid},
                {"$set": update_doc},
            )
            await emit_task_status(
                channel_id,
                {
                    "task_id": task_id,
                    "channel_id": channel_id,
                    "status": status,
                    **fields,
                },
            )

        try:
            # ── 1. Set status to running ──────────────────────────
            await _update_task(TaskStatus.running)

            # ── 2. Fetch channel info (repo_url, branch) ─────────
            channel = await db["channels"].find_one({"_id": ObjectId(channel_id)})
            if channel is None:
                await _update_task(
                    TaskStatus.failed,
                    result_summary="Channel not found",
                )
                return

            repo_url = channel.get("repo_url", "")
            branch = channel.get("default_branch", "main")

            if not repo_url:
                await _update_task(
                    TaskStatus.failed,
                    result_summary="Channel has no repo_url configured",
                )
                return

            # ── 3. Fetch agent info (system_prompt) ───────────────
            agent = await db["agents"].find_one({"_id": ObjectId(agent_id)})
            system_prompt = agent.get("system_prompt") if agent else None

            # ── 4. Build image & start container ──────────────────
            logger.info(
                "Starting container for task %s (agent=%s, channel=%s)",
                task_id,
                agent_id,
                channel_id,
            )
            container_id, container_name, host_port = await container_service.run_agent_container(
                agent_id=agent_id,
                channel_id=channel_id,
                repo_url=repo_url,
                branch=branch,
                github_token=settings.github_token,
                system_prompt=system_prompt,
            )

            # ── 5. Wait for agent runtime to be ready ─────────────
            ready = await container_service.wait_for_ready(
                container_name, host_port=host_port,
            )
            if not ready:
                await _update_task(
                    TaskStatus.failed,
                    result_summary="Agent container did not become ready (timeout)",
                )
                return

            # ── 6. Send task to agent runtime ─────────────────────
            logger.info(
                "Sending task %s to container %s",
                task_id,
                container_name,
            )
            result = await container_service.send_task(
                container_name=container_name,
                task_id=task_id,
                instruction=instruction,
                host_port=host_port,
            )

            # ── 7. Update task with results ───────────────────────
            await _update_task(
                TaskStatus.completed,
                result_summary=result.get("summary", ""),
                commit_sha=result.get("commit_sha"),
                pr_url=result.get("pr_url"),
                branch_name=result.get("branch_name"),
            )
            logger.info("Task %s completed successfully", task_id)

        except Exception:
            logger.exception("Task %s execution failed", task_id)
            import traceback

            error_summary = traceback.format_exc().split("\n")[-2][:500]
            await _update_task(
                TaskStatus.failed,
                result_summary=f"Execution error: {error_summary}",
            )

        finally:
            # ── 8. Cleanup container ──────────────────────────────
            if container_id:
                try:
                    await container_service.cleanup_container(container_id)
                except Exception:
                    logger.debug("Container cleanup error (ignored)", exc_info=True)
