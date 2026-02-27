"""FastAPI + Socket.IO application entry point."""

import os
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import close_connection, get_db
from app.routers import auth, bots, channels, dm, files
from app.routers.messages import channel_messages_router
from app.routers.messages import router as messages_router
from app.sockets import register_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure indexes
    db = get_db()
    await db["messages"].create_index([("content", "text")])
    await db["messages"].create_index("channel_id")
    await db["channels"].create_index("name")
    await db["bots"].create_index("owner_id")
    yield
    # Shutdown: close DB connection
    await close_connection()


# ── FastAPI app ──────────────────────────────────────────────
app = FastAPI(
    title="pioyan-chat API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (uploads) ────────────────────────────────────
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(channels.router, prefix="/api/channels", tags=["channels"])
# /api/channels/{channel_id}/messages  (GET + POST)
app.include_router(channel_messages_router, prefix="/api", tags=["messages"])
# /api/messages/search, /api/messages/{id}, /api/messages/{id}/thread
app.include_router(messages_router, prefix="/api/messages", tags=["messages"])
app.include_router(dm.router, prefix="/api/dm", tags=["dm"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(bots.router, prefix="/api/bots", tags=["bots"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# ── Socket.IO ─────────────────────────────────────────────────
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_origins,
    logger=False,
    engineio_logger=False,
)

register_handlers(sio)

# ASGI アプリとして Socket.IO を FastAPI の下にマウント
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
