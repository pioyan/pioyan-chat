"""Channels router: CRUD + member management."""

from datetime import UTC, datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.channel import ChannelCreate, ChannelPublic, ChannelUpdate
from app.models.user import UserPublic

router = APIRouter()


def _doc_to_channel(doc: dict) -> ChannelPublic:
    return ChannelPublic(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        is_private=doc.get("is_private", False),
        is_direct=doc.get("is_direct", False),
        members=[str(m) for m in doc.get("members", [])],
        created_by=str(doc["created_by"]),
        created_at=doc["created_at"],
    )


def _object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, Exception):
        raise HTTPException(status_code=404, detail="Not found") from None


@router.get("", response_model=list[ChannelPublic])
async def list_channels(
    current_user: UserPublic = Depends(get_current_user),
) -> list[ChannelPublic]:
    """Return all accessible channels (public + member-only private)."""
    db = get_db()
    user_oid = ObjectId(current_user.id)
    cursor = db["channels"].find(
        {
            "$or": [
                {"is_private": False},
                {"members": user_oid},
            ]
        }
    )
    return [_doc_to_channel(doc) async for doc in cursor]


@router.post("", response_model=ChannelPublic, status_code=201)
async def create_channel(
    body: ChannelCreate,
    current_user: UserPublic = Depends(get_current_user),
) -> ChannelPublic:
    """Create a new channel."""
    db = get_db()
    user_oid = ObjectId(current_user.id)
    now = datetime.now(UTC)
    doc = {
        "name": body.name,
        "description": body.description,
        "is_private": body.is_private,
        "members": [user_oid],
        "created_by": user_oid,
        "created_at": now,
    }
    result = await db["channels"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_channel(doc)


@router.get("/{channel_id}", response_model=ChannelPublic)
async def get_channel(
    channel_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> ChannelPublic:
    """Return a single channel by ID."""
    db = get_db()
    doc = await db["channels"].find_one({"_id": _object_id(channel_id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return _doc_to_channel(doc)


@router.put("/{channel_id}", response_model=ChannelPublic)
async def update_channel(
    channel_id: str,
    body: ChannelUpdate,
    current_user: UserPublic = Depends(get_current_user),
) -> ChannelPublic:
    """Update name/description of a channel."""
    db = get_db()
    oid = _object_id(channel_id)
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=422, detail="No fields to update")
    result = await db["channels"].find_one_and_update(
        {"_id": oid},
        {"$set": update_data},
        return_document=True,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return _doc_to_channel(result)


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(
    channel_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> None:
    """Delete a channel and its messages."""
    db = get_db()
    oid = _object_id(channel_id)
    result = await db["channels"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Channel not found")
    await db["messages"].delete_many({"channel_id": str(oid)})


class AddMemberRequest(BaseModel):
    user_id: str


@router.post("/{channel_id}/members", response_model=ChannelPublic)
async def add_member(
    channel_id: str,
    body: AddMemberRequest,
    current_user: UserPublic = Depends(get_current_user),
) -> ChannelPublic:
    """Add a user to a channel."""
    db = get_db()
    oid = _object_id(channel_id)
    member_oid = _object_id(body.user_id)
    result = await db["channels"].find_one_and_update(
        {"_id": oid},
        {"$addToSet": {"members": member_oid}},
        return_document=True,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return _doc_to_channel(result)


@router.delete("/{channel_id}/members/{user_id}", response_model=ChannelPublic)
async def remove_member(
    channel_id: str,
    user_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> ChannelPublic:
    """Remove a user from a channel."""
    db = get_db()
    oid = _object_id(channel_id)
    member_oid = _object_id(user_id)
    result = await db["channels"].find_one_and_update(
        {"_id": oid},
        {"$pull": {"members": member_oid}},
        return_document=True,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return _doc_to_channel(result)
