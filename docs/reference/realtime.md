# リアルタイム通信（Socket.IO）

pioyan-chat のリアルタイム通信は Socket.IO（WebSocket）で実現されています。

## 概要

```text
フロントエンド                           バックエンド
(socket.io-client)                     (python-socketio)

lib/socket.ts ──── WebSocket ─────→ sockets.py
hooks/useSocket.ts                      │
                                        ├─ connect    (JWT 検証)
                                        ├─ disconnect (オフライン通知)
                                        ├─ join_channel
                                        ├─ leave_channel
                                        ├─ new_message
                                        └─ typing
```

## 接続と認証

Socket.IO 接続時に JWT トークンで認証を行います。

### フロントエンド（接続）

```typescript
// lib/socket.ts
const socket = io("http://localhost:8000", {
  auth: { token: getToken() },
  transports: ["websocket"],
  autoConnect: false,
});
```

### バックエンド（認証検証）

```python
# sockets.py - connect イベント
async def connect(sid, environ, auth=None):
    token = auth.get("token") if auth else None
    user_id = decode_access_token(token)
    if user_id is None:
        return False  # 接続拒否
    _online_users[sid] = user_id
    await sio.emit("user_online", {"user_id": user_id})
    return True
```

トークンは以下の順序で取得を試みます:

1. `auth` パラメータ（`auth.token`）
2. クエリストリング（`?token=...`）

## イベント仕様

### `connect`

| 項目 | 内容 |
|------|------|
| 方向 | client → server |
| 認証 | JWT トークン必須 |
| 成功 | `user_online` イベントを全クライアントにブロードキャスト |
| 失敗 | 接続拒否（`return False`） |

### `disconnect`

| 項目 | 内容 |
|------|------|
| 方向 | client → server |
| 動作 | `user_offline` イベントを全クライアントにブロードキャスト |

### `join_channel`

| 項目 | 内容 |
|------|------|
| 方向 | client → server |
| ペイロード | `{ "channel_id": "..." }` |
| 動作 | Socket.IO ルームに参加 |

### `leave_channel`

| 項目 | 内容 |
|------|------|
| 方向 | client → server |
| ペイロード | `{ "channel_id": "..." }` |
| 動作 | Socket.IO ルームから退出 |

### `new_message`

| 項目 | 内容 |
|------|------|
| 方向 | bidirectional（client ↔ server） |
| ペイロード | `{ "channel_id": "...", "content": "...", ... }` |
| 動作 | 同じチャンネルルームの他メンバーにブロードキャスト（送信元は除外） |

### `typing`

| 項目 | 内容 |
|------|------|
| 方向 | bidirectional |
| ペイロード（送信） | `{ "channel_id": "..." }` |
| ペイロード（受信） | `{ "channel_id": "...", "user_id": "..." }` |
| 動作 | タイピング中であることを同じチャンネルルームに通知 |

### `user_online`

| 項目 | 内容 |
|------|------|
| 方向 | server → client |
| ペイロード | `{ "user_id": "..." }` |
| 発火タイミング | ユーザーが Socket.IO に接続した時 |

### `user_offline`

| 項目 | 内容 |
|------|------|
| 方向 | server → client |
| ペイロード | `{ "user_id": "..." }` |
| 発火タイミング | ユーザーが Socket.IO から切断した時 |

## ルーム管理

Socket.IO のルーム機能を使い、チャンネルごとにメッセージをスコープします。

```text
ルーム "channel_abc"
  ├── sid_1 (userA)
  ├── sid_2 (userB)
  └── sid_3 (userC)

userA が new_message を送信
  → userB, userC にブロードキャスト（userA は skip_sid で除外）
```

## オンラインユーザー管理

サーバー側でインメモリの `sid → user_id` マッピングを保持します。

```python
_online_users: dict[str, str] = {}
# connect 時: _online_users[sid] = user_id
# disconnect 時: _online_users.pop(sid)
```

> **注意**: MVP ではシングルプロセス前提です。  
> スケールアウト時は Redis Adapter を導入し、プロセス間でルームを共有する必要があります。

## フロントエンドのフック（`useSocket.ts`）

```typescript
// hooks/useSocket.ts
// Socket.IO イベントを React コンポーネントから購読するカスタムフック
import { useEffect } from "react";
import { getSocket } from "@/lib/socket";

export function useSocket(event: string, handler: (data: any) => void) {
  useEffect(() => {
    const socket = getSocket();
    socket.on(event, handler);
    return () => { socket.off(event, handler); };
  }, [event, handler]);
}
```

## CORS 設定

Socket.IO サーバーの `cors_allowed_origins` は FastAPI の `CORS_ORIGINS` 設定と同じ値を使用します。

```python
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=settings.cors_origins,  # ["http://localhost:3000"]
)
```
