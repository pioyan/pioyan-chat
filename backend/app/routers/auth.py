"""Auth router: signup / login / me."""

import contextlib
import io
import os
import uuid
from datetime import UTC, datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from PIL import Image
from pydantic import BaseModel, EmailStr

from app.auth.dependencies import get_current_user
from app.auth.utils import create_access_token, hash_password, verify_password
from app.config import settings
from app.database import get_db
from app.models.user import UserCreate, UserPublic, UserUpdate

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _doc_to_user(doc: dict) -> UserPublic:
    return UserPublic(
        id=str(doc["_id"]),
        username=doc["username"],
        email=doc["email"],
        avatar_url=doc.get("avatar_url"),
        created_at=doc["created_at"],
    )


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(body: UserCreate) -> TokenResponse:
    """Register a new user. username defaults to email if omitted."""
    db = get_db()
    # username のデフォルトはメールアドレス
    username = body.username if body.username else body.email

    # 重複チェック
    if await db["users"].find_one({"email": body.email}):
        raise HTTPException(status_code=409, detail="Email already registered")
    if await db["users"].find_one({"username": username}):
        raise HTTPException(status_code=409, detail="Username already taken")

    now = datetime.now(UTC)
    doc = {
        "username": username,
        "email": body.email,
        "hashed_password": hash_password(body.password),
        "avatar_url": None,
        "created_at": now,
    }
    result = await db["users"].insert_one(doc)
    token = create_access_token(str(result.inserted_id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest) -> TokenResponse:
    """Authenticate a user and return a JWT."""
    db = get_db()
    doc = await db["users"].find_one({"email": body.email})
    if doc is None or not verify_password(body.password, doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(str(doc["_id"]))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
async def me(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    """Return the currently authenticated user."""
    return current_user


@router.put("/me", response_model=UserPublic)
async def update_me(
    body: UserUpdate,
    current_user: UserPublic = Depends(get_current_user),
) -> UserPublic:
    """Update the current user's profile (username and/or avatar_url)."""
    db = get_db()
    update_data: dict = {}
    if body.username is not None:
        existing = await db["users"].find_one({"username": body.username})
        if existing and str(existing["_id"]) != current_user.id:
            raise HTTPException(status_code=409, detail="Username already taken")
        update_data["username"] = body.username
    if body.avatar_url is not None:
        update_data["avatar_url"] = body.avatar_url

    if update_data:
        await db["users"].update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": update_data},
        )
    doc = await db["users"].find_one({"_id": ObjectId(current_user.id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="User not found")
    return _doc_to_user(doc)


_AVATAR_SIZE = (256, 256)
_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


@router.post("/me/avatar", response_model=UserPublic)
async def upload_avatar(
    file: UploadFile,
    current_user: UserPublic = Depends(get_current_user),
) -> UserPublic:
    """Upload a profile image, resize it to 256×256, and save it locally."""
    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported image type. Use JPEG, PNG, GIF, or WebP.",
        )

    content = await file.read()

    try:
        img = Image.open(io.BytesIO(content))
    except (Image.UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=400, detail="Invalid image file.") from exc

    # thumbnail() はアスペクト比を保ちながら in-place でリサイズする
    img.thumbnail(_AVATAR_SIZE)

    # RGBA → RGB 変換（JPEG は透過をサポートしない）
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    output = io.BytesIO()
    img.save(output, format="JPEG", quality=85)
    resized_bytes = output.getvalue()

    stored_name = f"avatar_{uuid.uuid4().hex}.jpg"
    os.makedirs(settings.upload_dir, exist_ok=True)
    save_path = os.path.join(settings.upload_dir, stored_name)
    with open(save_path, "wb") as f:
        f.write(resized_bytes)

    avatar_url = f"/uploads/{stored_name}"
    db = get_db()

    # 古いアバターファイルを削除する
    old_doc = await db["users"].find_one({"_id": ObjectId(current_user.id)}, {"avatar_url": 1})
    if old_doc and isinstance(old_doc.get("avatar_url"), str):
        old_name = old_doc["avatar_url"].removeprefix("/uploads/")
        if old_name.startswith("avatar_"):
            old_path = os.path.join(settings.upload_dir, old_name)
            with contextlib.suppress(OSError):
                os.remove(old_path)

    await db["users"].update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"avatar_url": avatar_url}},
    )
    doc = await db["users"].find_one({"_id": ObjectId(current_user.id)})
    if doc is None:
        raise HTTPException(status_code=404, detail="User not found")
    return _doc_to_user(doc)
