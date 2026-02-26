"""Messages router: CRUD + pagination + search + thread."""

from datetime import UTC, datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.message import MessageCreate, MessagePublic
from app.models.user import UserPublic

# /api/channels/{channel_id}/messages に対応するルーター
channel_messages_router = APIRouter()
# /api/messages/* に対応するルーター
router = APIRouter()


def _doc_to_message(doc: dict) -> MessagePublic:
    return MessagePublic(
        id=str(doc["_id"]),
        channel_id=doc["channel_id"],
        sender_id=doc["sender_id"],
        content=doc["content"],
        file_url=doc.get("file_url"),
        thread_id=doc.get("thread_id"),
        reply_count=doc.get("reply_count", 0),
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
    )


def _object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, Exception):
        raise HTTPException(status_code=404, detail="Not found") from None


@router.get("/search", response_model=list[MessagePublic])
async def search_messages(
    q: str = Query(..., min_length=1),
    current_user: UserPublic = Depends(get_current_user),
) -> list[MessagePublic]:
    """Full-text search across messages."""
    db = get_db()
    cursor = (
        db["messages"]
        .find(
            {"$text": {"$search": q}},
            {"score": {"$meta": "textScore"}},
        )
        .sort([("score", {"$meta": "textScore"})])
        .limit(50)
    )
    return [_doc_to_message(doc) async for doc in cursor]


@channel_messages_router.get("/channels/{channel_id}/messages", response_model=list[MessagePublic])
async def list_messages(
    channel_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    before: str | None = Query(default=None),
    current_user: UserPublic = Depends(get_current_user),
) -> list[MessagePublic]:
    """Return messages for a channel, newest last, paginated."""
    db = get_db()
    query: dict = {"channel_id": channel_id, "thread_id": None}
    if before:
        query["_id"] = {"$lt": _object_id(before)}
    cursor = db["messages"].find(query).sort("created_at", 1).limit(limit)
    return [_doc_to_message(doc) async for doc in cursor]


@channel_messages_router.post(
    "/channels/{channel_id}/messages", response_model=MessagePublic, status_code=201
)
async def post_message(
    channel_id: str,
    body: MessageCreate,
    current_user: UserPublic = Depends(get_current_user),
) -> MessagePublic:
    """Post a new message to a channel."""
    db = get_db()
    now = datetime.now(UTC)
    doc = {
        "channel_id": channel_id,
        "sender_id": current_user.id,
        "content": body.content,
        "file_url": body.file_url,
        "thread_id": None,
        "reply_count": 0,
        "created_at": now,
        "updated_at": None,
    }
    result = await db["messages"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_message(doc)


@router.delete("/{message_id}", status_code=204)
async def delete_message(
    message_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> None:
    """Delete a message."""
    db = get_db()
    oid = _object_id(message_id)
    result = await db["messages"].delete_one({"_id": oid, "sender_id": current_user.id})
    if result.deleted_count == 0:
        # 所有者でない場合も含め 404 を返す
        raise HTTPException(status_code=404, detail="Message not found")


@router.get("/{message_id}/thread", response_model=list[MessagePublic])
async def get_thread(
    message_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> list[MessagePublic]:
    """Return thread replies for a message."""
    db = get_db()
    cursor = db["messages"].find({"thread_id": message_id}).sort("created_at", 1)
    return [_doc_to_message(doc) async for doc in cursor]


@router.post("/{message_id}/thread", response_model=MessagePublic, status_code=201)
async def post_thread_reply(
    message_id: str,
    body: MessageCreate,
    current_user: UserPublic = Depends(get_current_user),
) -> MessagePublic:
    """Post a reply to a message thread."""
    db = get_db()
    oid = _object_id(message_id)
    parent = await db["messages"].find_one({"_id": oid})
    if parent is None:
        raise HTTPException(status_code=404, detail="Parent message not found")

    now = datetime.now(UTC)
    doc = {
        "channel_id": parent["channel_id"],
        "sender_id": current_user.id,
        "content": body.content,
        "file_url": body.file_url,
        "thread_id": message_id,
        "reply_count": 0,
        "created_at": now,
        "updated_at": None,
    }
    result = await db["messages"].insert_one(doc)
    doc["_id"] = result.inserted_id
    # 親のreply_countをインクリメント
    await db["messages"].update_one({"_id": oid}, {"$inc": {"reply_count": 1}})
    return _doc_to_message(doc)
