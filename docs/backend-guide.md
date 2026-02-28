# バックエンドガイド

FastAPI + Socket.IO + Motor（非同期 MongoDB ドライバ）で構築されたバックエンドの設計と構成。

## ディレクトリ構成

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # エントリポイント (FastAPI + Socket.IO)
│   ├── config.py            # 環境変数設定 (pydantic-settings)
│   ├── database.py          # MongoDB 接続管理 (Motor)
│   ├── auth/
│   │   ├── utils.py         # JWT 生成・検証・パスワードハッシュ
│   │   └── dependencies.py  # get_current_user 依存関数
│   ├── models/
│   │   ├── user.py          # User モデル
│   │   ├── channel.py       # Channel モデル
│   │   ├── message.py       # Message モデル
│   │   └── bot.py           # Bot モデル
│   ├── routers/
│   │   ├── auth.py          # 認証 (signup / login / me)
│   │   ├── channels.py      # チャンネル CRUD + メンバー管理
│   │   ├── messages.py      # メッセージ CRUD + 検索 + スレッド
│   │   ├── dm.py            # ダイレクトメッセージ
│   │   ├── files.py         # ファイルアップロード
│   │   └── bots.py          # ボット CRUD
│   ├── bots/
│   │   └── validator.py     # Dockerfile バリデーター
│   └── sockets.py           # Socket.IO イベントハンドラ
├── tests/
│   ├── conftest.py          # pytest フィクスチャ
│   ├── test_auth.py
│   ├── test_channels.py
│   ├── test_messages.py
│   ├── test_dm.py
│   ├── test_files.py
│   ├── test_bots.py
│   ├── test_models.py
│   └── test_validator.py
├── uploads/                 # アップロードファイル保存先
├── container_files/         # ボット用コンテナファイル保存先
└── pyproject.toml           # 依存関係 + Ruff 設定
```

## エントリポイント（`main.py`）

```python
# FastAPI + Socket.IO の統合
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
```

起動コマンド:

```bash
python -m uvicorn app.main:socket_app --reload --port 8000
```

### ライフスパン（Startup / Shutdown）

- **Startup**: MongoDB インデックスの作成（テキスト検索用、チャンネル名、ボットオーナー）
- **Shutdown**: MongoDB 接続のクローズ

## ルーター一覧

| ルーター | プレフィックス | 説明 |
|---------|--------------|------|
| `auth.py` | `/api/auth` | ユーザー登録・ログイン・プロフィール |
| `channels.py` | `/api/channels` | チャンネル CRUD + メンバー管理 |
| `messages.py` | `/api/channels/{id}/messages`, `/api/messages` | メッセージ CRUD + 検索 + スレッド |
| `dm.py` | `/api/dm` | DM 会話一覧・開始・メッセージ取得 |
| `files.py` | `/api/files` | ファイルアップロード |
| `bots.py` | `/api/bots` | ボット CRUD + コンテナファイルバリデーション |

## 認証フロー

### JWT 認証

```text
Client                              Server
  │                                    │
  │  POST /api/auth/login              │
  │  { email, password }               │
  │ ──────────────────────────────────→ │
  │                                    │ パスワード検証 (bcrypt)
  │                                    │ JWT 生成 (HS256)
  │  { access_token, token_type }      │
  │ ←────────────────────────────────── │
  │                                    │
  │  GET /api/channels                 │
  │  Authorization: Bearer <token>     │
  │ ──────────────────────────────────→ │
  │                                    │ JWT 検証 → user_id 取得
  │  [channels...]                     │
  │ ←────────────────────────────────── │
```

### 依存関数

```python
# app/auth/dependencies.py
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    # JWT をデコードし、user_id からユーザーを取得
    ...
```

すべての保護エンドポイントで `Depends(get_current_user)` を使用します。

### パスワードハッシュ

- **ライブラリ**: passlib (bcrypt)
- ハッシュ生成: `get_password_hash(password)`
- 検証: `verify_password(plain, hashed)`

### JWT 設定

| 設定 | デフォルト | 説明 |
|------|----------|------|
| `JWT_SECRET` | `change-me-...` | 署名キー（本番では必ず変更） |
| `JWT_ALGORITHM` | `HS256` | 署名アルゴリズム |
| `JWT_EXPIRE_MINUTES` | `10080`（7日） | トークン有効期限 |

## データベース（`database.py`）

Motor（非同期 MongoDB ドライバ）を使用。

```python
from app.database import get_db

db = get_db()
users = db["users"]
channels = db["channels"]
messages = db["messages"]
bots = db["bots"]
```

### MongoDB コレクション

| コレクション | 用途 |
|------------|------|
| `users` | ユーザーアカウント |
| `channels` | チャンネル（DM を含む） |
| `messages` | メッセージ（スレッド返信を含む） |
| `bots` | コーディングボット |

### インデックス

| コレクション | インデックス | 用途 |
|------------|------------|------|
| `messages` | `content` (text) | テキスト検索 |
| `messages` | `channel_id` | チャンネル別メッセージ取得 |
| `channels` | `name` | チャンネル名検索 |
| `bots` | `owner_id` | オーナー別ボット取得 |

## ファイルアップロード

- アップロード先: `backend/uploads/`（`UPLOAD_DIR` で設定可能）
- 最大サイズ: 10MB（`MAX_FILE_SIZE_MB` で設定可能）
- ファイル名: UUID でリネーム（衝突防止）
- 静的配信: `/uploads/{filename}` パスで FastAPI の `StaticFiles` 経由

## ボットシステム

### Dockerfile バリデーション（`bots/validator.py`）

アップロードされた Dockerfile / Containerfile を解析し、安全性を検証します。

- 最大ファイルサイズ: 256KB（`MAX_CONTAINER_FILE_SIZE_KB`）
- 保存先: `backend/container_files/`

## テスト

pytest を使用。MongoDB サービスコンテナが必要です。

```bash
cd backend
pytest                    # 全テスト実行
pytest -v                 # 詳細出力
pytest tests/test_auth.py # 特定テストのみ
```

### テストフィクスチャ

`tests/conftest.py` でテスト用の MongoDB データベース・クライアントを提供します。

## Lint / Format

```bash
cd backend
ruff check .     # lint
ruff format .    # フォーマット
```
