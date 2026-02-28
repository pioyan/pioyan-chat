"""Socket.IO event handlers for pioyan-chat."""

from app.auth.utils import decode_access_token

# sio インスタンスは main.py から差し込む
_sio = None

# オンラインユーザー: sid -> user_id
_online_users: dict[str, str] = {}


def register_handlers(sio) -> None:
    """Register all Socket.IO event handlers on *sio*."""
    global _sio
    _sio = sio

    @sio.event
    async def connect(sid: str, environ: dict, auth: dict | None = None) -> bool:
        """Validate JWT on connect."""
        token = None
        if auth and isinstance(auth, dict):
            token = auth.get("token")
        if token is None:
            # クエリストリングからも試みる
            query = environ.get("QUERY_STRING", "")
            for part in query.split("&"):
                if part.startswith("token="):
                    token = part[len("token=") :]
                    break

        if token is None:
            return False  # 接続拒否

        user_id = decode_access_token(token)
        if user_id is None:
            return False

        _online_users[sid] = user_id
        await sio.emit("user_online", {"user_id": user_id})
        return True

    @sio.event
    async def disconnect(sid: str) -> None:
        user_id = _online_users.pop(sid, None)
        if user_id:
            await sio.emit("user_offline", {"user_id": user_id})

    @sio.event
    async def join_channel(sid: str, data: dict) -> None:
        """Join a Socket.IO room for a channel."""
        channel_id = data.get("channel_id")
        if channel_id:
            await sio.enter_room(sid, channel_id)

    @sio.event
    async def leave_channel(sid: str, data: dict) -> None:
        """Leave a Socket.IO room."""
        channel_id = data.get("channel_id")
        if channel_id:
            await sio.leave_room(sid, channel_id)

    @sio.event
    async def new_message(sid: str, data: dict) -> None:
        """Broadcast a new message to channel members."""
        channel_id = data.get("channel_id")
        if channel_id:
            await sio.emit("new_message", data, room=channel_id, skip_sid=sid)

    @sio.event
    async def typing(sid: str, data: dict) -> None:
        """Broadcast typing indicator."""
        channel_id = data.get("channel_id")
        if channel_id:
            user_id = _online_users.get(sid)
            await sio.emit(
                "typing",
                {"channel_id": channel_id, "user_id": user_id},
                room=channel_id,
                skip_sid=sid,
            )

    # ── Agent / Coding Task events ──────────────────────────────

    @sio.event
    async def agent_typing(sid: str, data: dict) -> None:
        """Broadcast agent typing indicator to a coding channel."""
        channel_id = data.get("channel_id")
        if channel_id:
            await sio.emit("agent_typing", data, room=channel_id)


async def emit_agent_response(channel_id: str, data: dict) -> None:
    """Emit an agent response to all clients in a coding channel.

    Called from the coding tasks execution pipeline when an agent
    produces output.
    """
    if _sio is not None:
        await _sio.emit("agent_response", data, room=channel_id)


async def emit_task_status(channel_id: str, data: dict) -> None:
    """Emit a task status update to all clients in a coding channel.

    Called when a coding task changes status (running, completed, failed).
    """
    if _sio is not None:
        await _sio.emit("task_status", data, room=channel_id)
