# API リファレンス

pioyan-chat バックエンドの REST API 全エンドポイントです。  
ベース URL: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

## 認証

すべての保護エンドポイントは `Authorization: Bearer <token>` ヘッダーが必要です。  
トークンは `/api/auth/login` または `/api/auth/signup` で取得できます。

---

## Auth

### `POST /api/auth/signup` — 新規ユーザー登録

**リクエスト**:

```json
{
  "email": "user@example.com",
  "password": "password123",
  "username": "user1"
}
```

`username` は省略可能（省略時はメールアドレスから自動生成）。

**レスポンス** `200`:

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### `POST /api/auth/login` — ログイン

**リクエスト**:

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**レスポンス** `200`:

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### `GET /api/auth/me` — 認証済みユーザー情報取得

**レスポンス** `200`:

```json
{
  "id": "...",
  "username": "user1",
  "email": "user@example.com",
  "avatar_url": null,
  "created_at": "2026-01-01T00:00:00Z"
}
```

### `PUT /api/auth/me` — プロフィール更新

**リクエスト**:

```json
{
  "username": "new_name",
  "avatar_url": "https://..."
}
```

### `POST /api/auth/me/avatar` — アバター画像アップロード

**リクエスト**: `multipart/form-data` で `file` フィールドに画像を送信。

---

## Channels

### `GET /api/channels` — チャンネル一覧取得

**レスポンス** `200`:

```json
[
  {
    "id": "...",
    "name": "general",
    "description": "一般チャンネル",
    "is_private": false,
    "is_direct": false,
    "members": [],
    "created_by": "user_id",
    "created_at": "2026-01-01T00:00:00Z"
  }
]
```

### `POST /api/channels` — チャンネル作成

**リクエスト**:

```json
{
  "name": "random",
  "description": "雑談チャンネル",
  "is_private": false
}
```

### `GET /api/channels/{id}` — チャンネル詳細取得

### `PUT /api/channels/{id}` — チャンネル更新

**リクエスト**:

```json
{
  "name": "renamed",
  "description": "更新後の説明"
}
```

### `DELETE /api/channels/{id}` — チャンネル削除

**レスポンス** `204`

### `POST /api/channels/{id}/members` — メンバー追加

**リクエスト**:

```json
{
  "user_id": "target_user_id"
}
```

### `DELETE /api/channels/{id}/members/{user_id}` — メンバー削除

---

## Messages

### `GET /api/channels/{channel_id}/messages` — メッセージ一覧取得

**クエリパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `limit` | int | 取得件数（デフォルト: 50） |
| `before` | string | このメッセージID より前のメッセージを取得 |

**レスポンス** `200`:

```json
[
  {
    "id": "...",
    "channel_id": "...",
    "sender_id": "...",
    "sender_username": "user1",
    "sender_avatar_url": null,
    "content": "Hello!",
    "file_url": null,
    "thread_id": null,
    "reply_count": 0,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

### `POST /api/channels/{channel_id}/messages` — メッセージ送信

**リクエスト**:

```json
{
  "content": "Hello!",
  "file_url": null
}
```

### `DELETE /api/messages/{id}` — メッセージ削除

### `GET /api/messages/{id}/thread` — スレッド取得

親メッセージに対する返信一覧を取得します。

### `POST /api/messages/{id}/thread` — スレッド返信

**リクエスト**:

```json
{
  "content": "返信内容",
  "file_url": null
}
```

### `GET /api/messages/search?q={keyword}` — メッセージ検索

MongoDB テキストインデックスによる全文検索です。

**クエリパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `q` | string | 検索キーワード |

---

## DM（ダイレクトメッセージ）

DM は `is_direct=True` のチャンネルとして内部的に管理されます。

### `GET /api/dm` — DM 会話一覧取得

### `POST /api/dm` — DM 会話開始

**リクエスト**:

```json
{
  "user_id": "target_user_id"
}
```

### `GET /api/dm/{conversation_id}/messages` — DM メッセージ一覧取得

---

## Files

### `POST /api/files/upload` — ファイルアップロード

**リクエスト**: `multipart/form-data` で `file` フィールドにファイルを送信。

**レスポンス** `200`:

```json
{
  "file_url": "/uploads/abcdef123456.txt"
}
```

ファイルはバックエンドの `uploads/` ディレクトリに保存され、  
`/uploads/{filename}` で静的配信されます。

**制限**: 最大 10MB（`MAX_FILE_SIZE_MB` で設定可能）

---

## Bots

### `POST /api/bots` — ボット登録

コンテナファイル（Dockerfile）のアップロードと合わせてボットを登録します。

**リクエスト**: `multipart/form-data`

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `name` | string | ボット名（1〜100文字） |
| `description` | string | 説明（省略可、最大500文字） |
| `container_file` | file | Dockerfile/Containerfile |

### `GET /api/bots` — ボット一覧取得

### `GET /api/bots/{id}` — ボット詳細取得

### `DELETE /api/bots/{id}` — ボット削除

### `POST /api/bots/validate` — コンテナファイルバリデーション

登録せずにコンテナファイルの妥当性を検証します。

---

## ヘルスチェック

### `GET /health`

**レスポンス** `200`:

```json
{
  "status": "ok"
}
```
