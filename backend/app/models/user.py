"""User Pydantic models."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=32)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserPublic(UserBase):
    id: str
    avatar_url: str | None = None
    created_at: datetime


class UserInDB(UserPublic):
    hashed_password: str
