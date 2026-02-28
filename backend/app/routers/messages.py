"""Messages router: CRUD + pagination + search + thread."""

import contextlib
import logging
from datetime import UTC, datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.coding_task import TaskStatus
from app.models.message import MessageCreate, MessagePublic
from app.models.user import UserPublic
from app.services.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

# /api/channels/{channel_id}/messages に対応するルーター
channel_messages_router = APIRouter()
# /api/messages/* に対応するルーター
router = APIRouter()


async def _user_map(db, sender_ids: list[str]) -> dict[str, dict]:
    """sender_id のリストからユーザー情報マップを返す。"""
    oids = []
    for sid in sender_ids:
        with contextlib.suppress(Exception):
            oids.append(ObjectId(sid))
    if not oids:
        return {}
    users = {}
    async for u in db["users"].find({"_id": {"$in": oids}}):
        users[str(u["_id"])] = u
    return users


def _doc_to_message(doc: dict, users: dict[str, dict] | None = None) -> MessagePublic:
    sender_id = doc["sender_id"]
    user = (users or {}).get(sender_id, {})
    sender_username: str = user.get("username") or user.get("email") or sender_id
    return MessagePublic(
        id=str(doc["_id"]),
        channel_id=doc["channel_id"],
        sender_id=sender_id,
        sender_username=sender_username,
        sender_avatar_url=user.get("avatar_url"),
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
    docs = [doc async for doc in cursor]
    users = await _user_map(db, [d["sender_id"] for d in docs])
    return [_doc_to_message(d, users) for d in docs]


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
    docs = [doc async for doc in cursor]
    users = await _user_map(db, [d["sender_id"] for d in docs])
    return [_doc_to_message(d, users) for d in docs]


@channel_messages_router.post(
    "/channels/{channel_id}/messages", response_model=MessagePublic, status_code=201
)
async def post_message(
    channel_id: str,
    body: MessageCreate,
    current_user: UserPublic = Depends(get_current_user),
) -> MessagePublic:
    """Post a new message to a channel.

    If the channel is a coding channel, automatically creates a coding task
    and routes the instruction to the appropriate agent.
    """
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
    users = {
        current_user.id: {"username": current_user.username, "avatar_url": current_user.avatar_url}
    }
    message = _doc_to_message(doc, users)

    # ── Coding channel auto-task creation ──
    await _maybe_create_coding_task(db, channel_id, body.content, current_user, now)

    return message


async def _maybe_create_coding_task(
    db, channel_id: str, content: str, user: UserPublic, now
) -> None:
    """If channel is a coding channel, create a task from the message."""
    try:
        ch_oid = ObjectId(channel_id)
    except Exception:
        return

    channel = await db["channels"].find_one({"_id": ch_oid})
    if channel is None or not channel.get("is_coding"):
        return

    agent_ids = channel.get("assigned_agents", [])
    available_agents: dict[str, str] = {}
    if agent_ids:
        cursor = db["agents"].find({"_id": {"$in": agent_ids}})
        async for agent_doc in cursor:
            available_agents[str(agent_doc["_id"])] = agent_doc["name"]

    if not available_agents:
        logger.warning("Coding channel %s has no agents assigned", channel_id)
        return

    routing = await Orchestrator.route_instruction(content, available_agents)
    if not routing["target_agent_ids"]:
        return

    task_doc = {
        "channel_id": ch_oid,
        "agent_id": ObjectId(routing["target_agent_ids"][0]),
        "user_id": ObjectId(user.id),
        "instruction": routing["instruction"],
        "status": TaskStatus.pending,
        "result_summary": None,
        "commit_sha": None,
        "pr_url": None,
        "branch_name": None,
        "created_at": now,
        "completed_at": None,
    }
    await db["coding_tasks"].insert_one(task_doc)
    logger.info(
        "Auto-created coding task in channel %s for agent %s",
        channel_id,
        routing["target_agent_ids"][0],
    )


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
    docs = [doc async for doc in cursor]
    users = await _user_map(db, [d["sender_id"] for d in docs])
    return [_doc_to_message(d, users) for d in docs]


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
    users = {
        current_user.id: {"username": current_user.username, "avatar_url": current_user.avatar_url}
    }
    return _doc_to_message(doc, users)
