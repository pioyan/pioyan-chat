# データモデル

pioyan-chat で使用するデータモデルの定義です。  
バックエンドは Pydantic モデル、フロントエンドは TypeScript 型として定義されています。

## User

ユーザーアカウント情報。

### Pydantic モデル（バックエンド）

```python
class UserCreate(BaseModel):
    username: str | None  # 省略時はメールから自動生成（2〜64文字）
    email: EmailStr
    password: str          # 最低8文字

class UserPublic(BaseModel):
    id: str
    username: str
    email: EmailStr
    avatar_url: str | None
    created_at: datetime

class UserInDB(UserPublic):
    hashed_password: str
```

### TypeScript 型（フロントエンド）

```typescript
interface User {
  id: string;
  username: string;
  email: string;
  avatar_url: string | null;
  created_at: string;
}
```

### MongoDB ドキュメント

コレクション: `users`

```json
{
  "_id": ObjectId("..."),
  "username": "user1",
  "email": "user@example.com",
  "hashed_password": "$2b$12$...",
  "avatar_url": null,
  "created_at": ISODate("2026-01-01T00:00:00Z")
}
```

---

## Channel

チャンネル（パブリック / プライベート / DM）。  
DM は `is_direct: true` + `members: [userA, userB]` のチャンネルとして表現します。

### Pydantic モデル（バックエンド）

```python
class ChannelCreate(BaseModel):
    name: str               # 1〜80文字
    description: str | None
    is_private: bool = False

class ChannelPublic(BaseModel):
    id: str
    name: str
    description: str | None
    is_private: bool
    is_direct: bool = False
    members: list[str] = []
    created_by: str
    created_at: datetime
```

### TypeScript 型（フロントエンド）

```typescript
interface Channel {
  id: string;
  name: string;
  description: string | null;
  is_private: boolean;
  is_direct: boolean;
  members: string[];
  created_by: string;
  created_at: string;
}
```

### MongoDB ドキュメント

コレクション: `channels`

```json
{
  "_id": ObjectId("..."),
  "name": "general",
  "description": "一般チャンネル",
  "is_private": false,
  "is_direct": false,
  "members": [],
  "created_by": "user_id",
  "created_at": ISODate("2026-01-01T00:00:00Z")
}
```

DM の例:

```json
{
  "_id": ObjectId("..."),
  "name": "dm_userA_userB",
  "is_private": true,
  "is_direct": true,
  "members": ["userA_id", "userB_id"],
  "created_by": "userA_id",
  "created_at": ISODate("2026-01-01T00:00:00Z")
}
```

---

## Message

メッセージ。スレッド返信は `thread_id` で親メッセージを参照します。

### Pydantic モデル（バックエンド）

```python
class MessageCreate(BaseModel):
    content: str            # 1〜4000文字
    file_url: str | None

class MessagePublic(BaseModel):
    id: str
    channel_id: str
    sender_id: str
    sender_username: str
    sender_avatar_url: str | None
    content: str
    file_url: str | None
    thread_id: str | None   # スレッド返信の場合は親メッセージID
    reply_count: int = 0
    created_at: datetime
    updated_at: datetime | None
```

### TypeScript 型（フロントエンド）

```typescript
interface Message {
  id: string;
  channel_id: string;
  sender_id: string;
  sender_username: string;
  sender_avatar_url: string | null;
  content: string;
  file_url: string | null;
  thread_id: string | null;
  reply_count: number;
  created_at: string;
  updated_at: string | null;
}
```

### MongoDB ドキュメント

コレクション: `messages`

```json
{
  "_id": ObjectId("..."),
  "channel_id": "channel_id",
  "sender_id": "user_id",
  "sender_username": "user1",
  "content": "Hello!",
  "file_url": null,
  "thread_id": null,
  "reply_count": 0,
  "created_at": ISODate("2026-01-01T00:00:00Z"),
  "updated_at": null
}
```

### インデックス

```python
# テキスト検索用
db["messages"].create_index([("content", "text")])
# チャンネル別取得の高速化
db["messages"].create_index("channel_id")
```

---

## Bot

コーディングボット（コンテナベース）。

### Pydantic モデル（バックエンド）

```python
class BotStatus(StrEnum):
    registered = "registered"
    building = "building"
    ready = "ready"
    error = "error"

class BotCreate(BaseModel):
    name: str               # 1〜100文字
    description: str | None  # 最大500文字

class BotPublic(BaseModel):
    id: str
    name: str
    description: str | None
    owner_id: str
    container_file_name: str
    status: BotStatus = BotStatus.registered
    created_at: datetime
```

### TypeScript 型（フロントエンド）

```typescript
interface Bot {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  container_file_name: string;
  status: "registered" | "building" | "ready" | "error";
  created_at: string;
}
```

### MongoDB ドキュメント

コレクション: `bots`

```json
{
  "_id": ObjectId("..."),
  "name": "my-bot",
  "description": "コーディング支援ボット",
  "owner_id": "user_id",
  "container_file_name": "abc123_Dockerfile",
  "status": "registered",
  "created_at": ISODate("2026-01-01T00:00:00Z")
}
```

### インデックス

```python
db["bots"].create_index("owner_id")
```

---

## 認証トークン

### TypeScript 型

```typescript
interface AuthTokenResponse {
  access_token: string;
  token_type: string;  // "bearer"
}
```
