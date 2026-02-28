"""Agents router: CRUD + channel assignment."""

from datetime import UTC, datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.agent import AgentCreate, AgentPublic, AgentSource, AgentStatus
from app.models.user import UserPublic

router = APIRouter()


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


@router.post("", response_model=AgentPublic, status_code=201)
async def create_agent(
    body: AgentCreate,
    current_user: UserPublic = Depends(get_current_user),
) -> AgentPublic:
    """Register a new coding agent."""
    db = get_db()
    now = datetime.now(UTC)
    doc = {
        "name": body.name,
        "description": body.description,
        "system_prompt": body.system_prompt,
        "source": AgentSource.manual,
        "repo_agent_path": None,
        "status": AgentStatus.registered,
        "owner_id": ObjectId(current_user.id),
        "created_at": now,
    }
    result = await db["agents"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_agent(doc)


@router.get("", response_model=list[AgentPublic])
async def list_agents(
    current_user: UserPublic = Depends(get_current_user),
) -> list[AgentPublic]:
    """List agents owned by the current user."""
    db = get_db()
    cursor = db["agents"].find({"owner_id": ObjectId(current_user.id)})
    return [_doc_to_agent(doc) async for doc in cursor]


@router.get("/{agent_id}", response_model=AgentPublic)
async def get_agent(
    agent_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> AgentPublic:
    """Get a single agent by ID."""
    db = get_db()
    doc = await db["agents"].find_one(
        {
            "_id": _object_id(agent_id),
            "owner_id": ObjectId(current_user.id),
        }
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return _doc_to_agent(doc)


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(
    agent_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> None:
    """Delete an agent."""
    db = get_db()
    result = await db["agents"].delete_one(
        {
            "_id": _object_id(agent_id),
            "owner_id": ObjectId(current_user.id),
        }
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
