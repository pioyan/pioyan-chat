"""Coding tasks router — submit and track coding instructions."""

import logging
from datetime import UTC, datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.coding_task import CodingTaskCreate, CodingTaskPublic, TaskStatus
from app.models.user import UserPublic
from app.services.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

router = APIRouter()


def _doc_to_task(doc: dict) -> CodingTaskPublic:
    return CodingTaskPublic(
        id=str(doc["_id"]),
        channel_id=str(doc["channel_id"]),
        agent_id=str(doc["agent_id"]),
        user_id=str(doc["user_id"]),
        instruction=doc["instruction"],
        status=doc.get("status", TaskStatus.pending),
        result_summary=doc.get("result_summary"),
        commit_sha=doc.get("commit_sha"),
        pr_url=doc.get("pr_url"),
        branch_name=doc.get("branch_name"),
        created_at=doc["created_at"],
        completed_at=doc.get("completed_at"),
    )


def _object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, Exception):
        raise HTTPException(status_code=404, detail="Not found") from None


@router.post("/{channel_id}/tasks", response_model=CodingTaskPublic, status_code=201)
async def create_coding_task(
    channel_id: str,
    body: CodingTaskCreate,
    background_tasks: BackgroundTasks,
    current_user: UserPublic = Depends(get_current_user),
) -> CodingTaskPublic:
    """Submit a coding instruction to a coding channel.

    The instruction is routed to the appropriate agent based on @mentions.
    If no mention is found, the orchestrator selects the best agent.
    """
    db = get_db()
    ch_oid = _object_id(channel_id)

    # Verify channel is a coding channel
    channel = await db["channels"].find_one({"_id": ch_oid})
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if not channel.get("is_coding"):
        raise HTTPException(status_code=400, detail="Not a coding channel")

    # Build agent name→id mapping from assigned agents
    agent_ids = channel.get("assigned_agents", [])
    available_agents: dict[str, str] = {}
    if agent_ids:
        cursor = db["agents"].find({"_id": {"$in": agent_ids}})
        async for agent_doc in cursor:
            available_agents[str(agent_doc["_id"])] = agent_doc["name"]

    # If agent_id is explicitly provided, use it
    if body.agent_id:
        target_agent_id = body.agent_id
        instruction = body.instruction
    else:
        # Route via orchestrator
        routing = await Orchestrator.route_instruction(body.instruction, available_agents)
        if not routing["target_agent_ids"]:
            raise HTTPException(
                status_code=400,
                detail="No agents available in this channel",
            )
        target_agent_id = routing["target_agent_ids"][0]
        instruction = routing["instruction"]

    now = datetime.now(UTC)
    doc = {
        "channel_id": ch_oid,
        "agent_id": ObjectId(target_agent_id),
        "user_id": ObjectId(current_user.id),
        "instruction": instruction,
        "status": TaskStatus.pending,
        "result_summary": None,
        "commit_sha": None,
        "pr_url": None,
        "branch_name": None,
        "created_at": now,
        "completed_at": None,
    }
    result = await db["coding_tasks"].insert_one(doc)
    doc["_id"] = result.inserted_id

    # Phase 4E: trigger container execution asynchronously
    background_tasks.add_task(
        Orchestrator.execute_task,
        task_id=str(result.inserted_id),
        channel_id=channel_id,
        agent_id=target_agent_id,
        instruction=instruction,
    )

    return _doc_to_task(doc)


@router.get("/{channel_id}/tasks", response_model=list[CodingTaskPublic])
async def list_coding_tasks(
    channel_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> list[CodingTaskPublic]:
    """List coding tasks for a channel."""
    db = get_db()
    ch_oid = _object_id(channel_id)

    cursor = db["coding_tasks"].find({"channel_id": ch_oid}).sort("created_at", -1)
    return [_doc_to_task(doc) async for doc in cursor]


@router.get("/{channel_id}/tasks/{task_id}", response_model=CodingTaskPublic)
async def get_coding_task(
    channel_id: str,
    task_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> CodingTaskPublic:
    """Get details of a specific coding task."""
    db = get_db()
    doc = await db["coding_tasks"].find_one(
        {
            "_id": _object_id(task_id),
            "channel_id": _object_id(channel_id),
        }
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return _doc_to_task(doc)
