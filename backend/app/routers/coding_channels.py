"""Coding channels router: creation + agent assignment."""

from datetime import UTC, datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.agent import AgentPublic, AgentSource, AgentStatus
from app.models.channel import ChannelPublic, CodingChannelCreate
from app.models.user import UserPublic
from app.services.github_service import GitHubService

router = APIRouter()


def _doc_to_channel(doc: dict) -> ChannelPublic:
    return ChannelPublic(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        is_private=doc.get("is_private", False),
        is_direct=doc.get("is_direct", False),
        is_coding=doc.get("is_coding", False),
        members=[str(m) for m in doc.get("members", [])],
        repo_url=doc.get("repo_url"),
        repo_owner=doc.get("repo_owner"),
        repo_name=doc.get("repo_name"),
        default_branch=doc.get("default_branch", "main"),
        assigned_agents=[str(a) for a in doc.get("assigned_agents", [])],
        created_by=str(doc["created_by"]),
        created_at=doc["created_at"],
    )


def _doc_to_agent(doc: dict) -> AgentPublic:
    return AgentPublic(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        system_prompt=doc.get("system_prompt"),
        source=doc.get("source", AgentSource.manual),
        repo_agent_path=doc.get("repo_agent_path"),
        status=doc.get("status", AgentStatus.registered),
        owner_id=str(doc["owner_id"]),
        created_at=doc["created_at"],
    )


def _object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, Exception):
        raise HTTPException(status_code=404, detail="Not found") from None


@router.post("/coding", response_model=ChannelPublic, status_code=201)
async def create_coding_channel(
    body: CodingChannelCreate,
    current_user: UserPublic = Depends(get_current_user),
) -> ChannelPublic:
    """Create a coding channel linked to a GitHub repository."""
    db = get_db()
    user_oid = ObjectId(current_user.id)
    now = datetime.now(UTC)

    repo_owner, repo_name = GitHubService.parse_repo_url(body.repo_url)

    doc = {
        "name": body.name,
        "description": body.description,
        "is_private": True,  # coding channels are private by default
        "is_direct": False,
        "is_coding": True,
        "members": [user_oid],
        "repo_url": body.repo_url,
        "repo_owner": repo_owner,
        "repo_name": repo_name,
        "default_branch": body.default_branch,
        "assigned_agents": [],
        "created_by": user_oid,
        "created_at": now,
    }
    result = await db["channels"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_channel(doc)


@router.post("/{channel_id}/agents/{agent_id}", response_model=ChannelPublic)
async def assign_agent_to_channel(
    channel_id: str,
    agent_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> ChannelPublic:
    """Assign an agent to a coding channel."""
    db = get_db()
    ch_oid = _object_id(channel_id)
    agent_oid = _object_id(agent_id)

    # Verify channel exists and is a coding channel
    channel = await db["channels"].find_one({"_id": ch_oid})
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if not channel.get("is_coding"):
        raise HTTPException(
            status_code=400, detail="Agents can only be assigned to coding channels"
        )

    # Verify agent exists
    agent = await db["agents"].find_one({"_id": agent_oid})
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    result = await db["channels"].find_one_and_update(
        {"_id": ch_oid},
        {"$addToSet": {"assigned_agents": agent_oid}},
        return_document=True,
    )
    return _doc_to_channel(result)


@router.delete("/{channel_id}/agents/{agent_id}", response_model=ChannelPublic)
async def remove_agent_from_channel(
    channel_id: str,
    agent_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> ChannelPublic:
    """Remove an agent from a coding channel."""
    db = get_db()
    ch_oid = _object_id(channel_id)
    agent_oid = _object_id(agent_id)

    result = await db["channels"].find_one_and_update(
        {"_id": ch_oid},
        {"$pull": {"assigned_agents": agent_oid}},
        return_document=True,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return _doc_to_channel(result)


@router.get("/{channel_id}/agents", response_model=list[AgentPublic])
async def list_channel_agents(
    channel_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> list[AgentPublic]:
    """List all agents assigned to a channel."""
    db = get_db()
    ch_oid = _object_id(channel_id)

    channel = await db["channels"].find_one({"_id": ch_oid})
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")

    agent_ids = channel.get("assigned_agents", [])
    if not agent_ids:
        return []

    cursor = db["agents"].find({"_id": {"$in": agent_ids}})
    return [_doc_to_agent(doc) async for doc in cursor]
