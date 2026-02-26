"""Auth router: signup / login / me."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.auth.dependencies import get_current_user
from app.auth.utils import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.user import UserCreate, UserPublic

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/signup", response_model=TokenResponse, status_code=201)
async def signup(body: UserCreate) -> TokenResponse:
    """Register a new user."""
    db = get_db()
    # 重複チェック
    if await db["users"].find_one({"email": body.email}):
        raise HTTPException(status_code=409, detail="Email already registered")
    if await db["users"].find_one({"username": body.username}):
        raise HTTPException(status_code=409, detail="Username already taken")

    now = datetime.now(UTC)
    doc = {
        "username": body.username,
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
