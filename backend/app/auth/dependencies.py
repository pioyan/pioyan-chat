"""FastAPI dependency: get_current_user from Bearer JWT."""

from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.utils import decode_access_token
from app.database import get_db
from app.models.user import UserPublic

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> UserPublic:
    """Validate JWT and return the authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = credentials.credentials
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    db = get_db()
    doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if doc is None:
        raise credentials_exception

    return UserPublic(
        id=str(doc["_id"]),
        username=doc["username"],
        email=doc["email"],
        avatar_url=doc.get("avatar_url"),
        created_at=doc["created_at"],
    )
