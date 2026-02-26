"""User Pydantic models."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=64)
    email: EmailStr


class UserCreate(BaseModel):
    """Signup payload. username defaults to email if omitted."""

    username: str | None = Field(default=None, min_length=2, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Profile update payload."""

    username: str | None = Field(default=None, min_length=2, max_length=64)
    avatar_url: str | None = None


class UserPublic(UserBase):
    id: str
    avatar_url: str | None = None
    created_at: datetime


class UserInDB(UserPublic):
    hashed_password: str
