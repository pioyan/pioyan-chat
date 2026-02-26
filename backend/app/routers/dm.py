"""DM router: Direct Messages implemented as private channels."""

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.channel import ChannelPublic
from app.models.message import MessagePublic
from app.models.user import UserPublic
from app.routers.channels import _doc_to_channel, _object_id
from app.routers.messages import _doc_to_message

router = APIRouter()


class StartDMRequest(BaseModel):
    user_id: str


@router.get("", response_model=list[ChannelPublic])
async def list_dms(
    current_user: UserPublic = Depends(get_current_user),
) -> list[ChannelPublic]:
    """Return all DM conversations for the current user."""
    db = get_db()
    user_oid = ObjectId(current_user.id)
    cursor = db["channels"].find({"is_direct": True, "members": user_oid})
    return [_doc_to_channel(doc) async for doc in cursor]


@router.post("", response_model=ChannelPublic, status_code=201)
async def start_dm(
    body: StartDMRequest,
    current_user: UserPublic = Depends(get_current_user),
) -> ChannelPublic:
    """Start (or retrieve existing) DM with another user."""
    db = get_db()
    user_oid = ObjectId(current_user.id)
    other_oid = _object_id(body.user_id)

    # 既存のDMを探す（メンバーが2人かつ is_direct=True）
    existing = await db["channels"].find_one(
        {
            "is_direct": True,
            "members": {"$all": [user_oid, other_oid], "$size": 2},
        }
    )
    if existing:
        return _doc_to_channel(existing)

    from datetime import UTC, datetime

    now = datetime.now(UTC)
    doc = {
        "name": f"dm-{current_user.id}-{body.user_id}",
        "description": None,
        "is_private": True,
        "is_direct": True,
        "members": [user_oid, other_oid],
        "created_by": user_oid,
        "created_at": now,
    }
    result = await db["channels"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_channel(doc)


@router.get("/{conversation_id}/messages", response_model=list[MessagePublic])
async def get_dm_messages(
    conversation_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> list[MessagePublic]:
    """Return messages in a DM conversation."""
    db = get_db()
    user_oid = ObjectId(current_user.id)
    conv_oid = _object_id(conversation_id)
    # アクセス権チェック
    conv = await db["channels"].find_one({"_id": conv_oid, "is_direct": True, "members": user_oid})
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    cursor = db["messages"].find({"channel_id": conversation_id}).sort("created_at", 1)
    return [_doc_to_message(doc) async for doc in cursor]
