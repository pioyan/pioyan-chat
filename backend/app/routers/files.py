"""Files router: file upload."""

import os
import uuid

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.config import settings
from app.models.user import UserPublic

router = APIRouter()


class FileUploadResponse(BaseModel):
    filename: str
    file_url: str
    size: int


@router.post("/upload", response_model=FileUploadResponse, status_code=201)
async def upload_file(
    file: UploadFile,
    current_user: UserPublic = Depends(get_current_user),
) -> FileUploadResponse:
    """Upload a file and return its URL."""
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.max_file_size_mb} MB",
        )

    # ユニークなファイル名を生成
    ext = os.path.splitext(file.filename or "")[1]
    stored_name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(settings.upload_dir, stored_name)

    os.makedirs(settings.upload_dir, exist_ok=True)
    async with aiofiles.open(save_path, "wb") as f:
        await f.write(content)

    return FileUploadResponse(
        filename=file.filename or stored_name,
        file_url=f"/uploads/{stored_name}",
        size=len(content),
    )
