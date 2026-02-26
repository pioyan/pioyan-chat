"""Bots router: coding bot registration with container file upload."""

import os
import uuid
from datetime import UTC, datetime

import aiofiles
from bson import ObjectId
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user
from app.bots.validator import validate_container_file
from app.config import settings
from app.database import get_db
from app.models.bot import BotPublic, BotStatus
from app.models.user import UserPublic

router = APIRouter()

# ── Request / Response models ─────────────────────────────────


class BotCreateRequest(BaseModel):
    """Multipart-compatible model; actual fields come as form data."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class BotValidateResponse(BaseModel):
    valid: bool
    errors: list[str] = []


# ── Helpers ────────────────────────────────────────────────────


def _doc_to_public(doc: dict) -> BotPublic:
    return BotPublic(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        owner_id=doc["owner_id"],
        container_file_name=doc["container_file_name"],
        status=doc.get("status", BotStatus.registered),
        created_at=doc["created_at"],
    )


# ── Endpoints ──────────────────────────────────────────────────


@router.post("", response_model=BotPublic, status_code=201)
async def register_bot(
    name: str = Form(..., min_length=1, max_length=100),
    container_file: UploadFile = ...,
    description: str | None = Form(default=None, max_length=500),
    current_user: UserPublic = Depends(get_current_user),
) -> BotPublic:
    """Register a new coding bot with a container definition file."""
    # ── Read & validate container file ─────────────────────────
    max_bytes = settings.max_container_file_size_kb * 1024
    content = await container_file.read()

    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Container file too large. Maximum size is {settings.max_container_file_size_kb} KB",
        )

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as err:
        raise HTTPException(
            status_code=422,
            detail="Container file must be a valid UTF-8 text file",
        ) from err

    errors = validate_container_file(text)
    if errors:
        raise HTTPException(status_code=422, detail={"validation_errors": errors})

    # ── Persist container file ─────────────────────────────────
    original_name = container_file.filename or "Dockerfile"
    stored_name = f"{uuid.uuid4().hex}_{original_name}"
    save_dir = settings.container_files_dir
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, stored_name)
    async with aiofiles.open(save_path, "wb") as f:
        await f.write(content)

    # ── Insert into DB ─────────────────────────────────────────
    db = get_db()
    doc = {
        "name": name,
        "description": description,
        "owner_id": current_user.id,
        "container_file_name": original_name,
        "container_file_path": save_path,
        "status": BotStatus.registered.value,
        "created_at": datetime.now(UTC),
    }
    result = await db["bots"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_public(doc)


@router.get("", response_model=list[BotPublic])
async def list_bots(
    current_user: UserPublic = Depends(get_current_user),
) -> list[BotPublic]:
    """List bots owned by the current user."""
    db = get_db()
    cursor = db["bots"].find({"owner_id": current_user.id}).sort("created_at", -1)
    return [_doc_to_public(doc) async for doc in cursor]


@router.get("/{bot_id}", response_model=BotPublic)
async def get_bot(
    bot_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> BotPublic:
    """Get details of a specific bot."""
    db = get_db()
    doc = await db["bots"].find_one({"_id": ObjectId(bot_id), "owner_id": current_user.id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    return _doc_to_public(doc)


@router.delete("/{bot_id}", status_code=204)
async def delete_bot(
    bot_id: str,
    current_user: UserPublic = Depends(get_current_user),
) -> None:
    """Delete a bot and its container file."""
    db = get_db()
    doc = await db["bots"].find_one({"_id": ObjectId(bot_id), "owner_id": current_user.id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Remove container file from disk
    file_path = doc.get("container_file_path")
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

    await db["bots"].delete_one({"_id": ObjectId(bot_id)})


@router.post("/validate", response_model=BotValidateResponse)
async def validate_container(
    container_file: UploadFile,
    current_user: UserPublic = Depends(get_current_user),
) -> BotValidateResponse:
    """Validate a container file without registering a bot."""
    max_bytes = settings.max_container_file_size_kb * 1024
    content = await container_file.read()

    if len(content) > max_bytes:
        return BotValidateResponse(
            valid=False,
            errors=[
                f"Container file too large. Maximum size is {settings.max_container_file_size_kb} KB"
            ],
        )

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return BotValidateResponse(
            valid=False,
            errors=["Container file must be a valid UTF-8 text file"],
        )

    errors = validate_container_file(text)
    return BotValidateResponse(valid=len(errors) == 0, errors=errors)
