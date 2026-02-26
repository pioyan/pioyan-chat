# チャットアプリケーション構築計画

## 概要

Slack / RocketChat ライクなリアルタイムチャットアプリ MVP の構築計画。
単一リポジトリ内で `frontend/`（Next.js）と `backend/`（FastAPI）をディレクトリ分離し、
Docker Compose で MongoDB を起動する構成。

## 技術スタック

| レイヤー         | 技術                         | 補足                        |
|-----------------|-----------------------------|-----------------------------|
| フロントエンド    | Next.js 15 (React) + TypeScript | App Router, Tailwind CSS    |
| バックエンド      | Python + FastAPI            | uvicorn ASGI サーバー         |
| リアルタイム通信  | Socket.IO (python-socketio + socket.io-client) | WebSocket |
| データベース      | MongoDB 7                   | Motor（非同期ドライバ）        |
| 認証             | JWT (python-jose + passlib) | メール＋パスワード ＋ Bearer トークン |
| パッケージ管理    | pnpm (Node.js) / pip (Python) |                             |
| コンテナ          | Docker Compose              | MongoDB のみコンテナ化         |
| Linter/Formatter | ESLint + Prettier (TS) / Ruff (Python) |               |
| テスト            | Vitest + RTL (TS) / pytest (Python) |                  |

## ディレクトリ構成（最終形）

```text
pioyan-chat/
├── frontend/               # Next.js (React) アプリ
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/     # ログイン・サインアップ
│   │   │   └── (chat)/     # チャット本体
│   │   ├── components/     # 再利用可能な UI コンポーネント
│   │   ├── hooks/          # カスタム React フック
│   │   ├── lib/            # utl / api / auth / socket
│   │   └── stores/         # Zustand ストア
│   ├── package.json
│   └── vitest.config.ts
├── backend/                # FastAPI アプリ
│   ├── app/
│   │   ├── main.py         # エントリポイント (FastAPI + Socket.IO)
│   │   ├── config.py       # 環境変数設定 (pydantic-settings)
│   │   ├── database.py     # MongoDB 接続管理 (Motor)
│   │   ├── auth/           # JWT 生成・検証・パスワードハッシュ
│   │   ├── models/         # Pydantic モデル (User, Channel, Message)
│   │   ├── routers/        # FastAPI Router (auth, channels, messages, dm, files)
│   │   └── sockets.py      # Socket.IO イベントハンドラ
│   ├── tests/              # pytest テスト
│   ├── uploads/            # アップロードファイル置き場（MVP）
│   └── pyproject.toml
├── docker-compose.yml      # MongoDB サービス定義
├── .devcontainer/
│   └── devcontainer.json   # pnpm + Python 追加・postCreateCommand 更新
├── .github/
│   └── workflows/
│       └── ci.yml          # 既存衛生チェック + 言語固有ジョブ追加
└── .vscode/
    └── settings.json       # Hooks に Ruff / ESLint fix を追加
```

## 機能スコープ（MVP）

| 機能                              | 優先度 |
|----------------------------------|--------|
| ユーザー認証（サインアップ / ログイン） | Must   |
| チャンネル（パブリック / プライベート）  | Must   |
| リアルタイムメッセージ送受信             | Must   |
| ダイレクトメッセージ（DM）              | Must   |
| ファイルアップロード・画像共有           | Should |
| メッセージ検索                        | Should |
| スレッド（返信）                       | Should |
| オンラインステータス表示               | Should |
| タイピングインジケーター                | Could  |

## 実装フェーズ

### Phase 0: 開発環境・インフラ基盤

- [x] PLAN.md 作成（本ファイル）
- [x] `docker-compose.yml` 作成（MongoDB 7）
- [x] `.devcontainer/devcontainer.json` 更新（Node.js Feature + Python Feature + postCreateCommand）
- [x] `.vscode/settings.json` 更新（Ruff / ESLint Hooks 追加）
- [x] `.github/dependabot.yml` 更新（npm `frontend/` + pip `backend/` 有効化）
- [x] `.github/workflows/ci.yml` 更新（言語固有テスト・lint ジョブ追加）
- [x] `.env.example` 作成

### Phase 1: バックエンド（FastAPI）

- [x] `backend/pyproject.toml` 作成（依存一覧 + Ruff 設定）
- [x] `backend/app/main.py` — FastAPI + Socket.IO 統合エントリポイント
- [x] `backend/app/config.py` — pydantic-settings 環境変数
- [x] `backend/app/database.py` — Motor MongoDB 接続管理
- [x] `backend/app/models/` — User, Channel, Message Pydantic モデル（TDD）
- [x] `backend/app/auth/` — JWT, パスワードハッシュ（TDD）
- [x] `backend/app/routers/auth.py` — signup / login / me（TDD）
- [x] `backend/app/routers/channels.py` — チャンネル CRUD + メンバー管理（TDD）
- [x] `backend/app/routers/messages.py` — メッセージ CRUD + 検索 + スレッド（TDD）
- [x] `backend/app/routers/dm.py` — DM（TDD）
- [x] `backend/app/routers/files.py` — ファイルアップロード（TDD）
- [x] `backend/app/sockets.py` — Socket.IO イベント（TDD）

### Phase 2: フロントエンド（Next.js）

- [x] `pnpm create next-app frontend` + 追加依存インストール
- [x] レイアウト・Slack 風 3 カラムデザイン
- [x] 認証画面（ログイン / サインアップ）
- [x] JWT 管理 (`lib/auth.ts`) + Next.js Middleware
- [x] `MessageList.tsx` / `MessageInput.tsx` / `MessageItem.tsx`
- [x] `Sidebar.tsx` — チャンネル・DM リスト
- [x] `ThreadPanel.tsx` — スレッドビュー
- [x] Socket.IO クライアント (`lib/socket.ts` + `hooks/useSocket.ts`)
- [x] Zustand ストア (`stores/chatStore.ts`)
- [x] 検索モーダル / ファイルアップロード UI
- [x] Vitest テスト

### Phase 3: CI / Dependabot / ドキュメント

- [x] CI に `backend-test` / `backend-lint` / `frontend-test` / `frontend-lint` / `frontend-build` ジョブ追加
- [x] Dependabot 有効化
- [x] README.md 書き替え
- [x] `human_docs/architecture.md` 更新

## API エンドポイント一覧

### 認証

| Method | Path             | 説明                  |
|--------|------------------|-----------------------|
| POST   | /api/auth/signup | 新規登録               |
| POST   | /api/auth/login  | ログイン（JWT 発行）   |
| GET    | /api/auth/me     | 認証済みユーザー情報取得 |

### チャンネル

| Method | Path                                   | 説明                   |
|--------|----------------------------------------|------------------------|
| GET    | /api/channels                          | チャンネル一覧           |
| POST   | /api/channels                          | チャンネル作成           |
| GET    | /api/channels/{id}                     | チャンネル詳細           |
| PUT    | /api/channels/{id}                     | チャンネル更新           |
| DELETE | /api/channels/{id}                     | チャンネル削除           |
| POST   | /api/channels/{id}/members             | メンバー追加             |
| DELETE | /api/channels/{id}/members/{user_id}   | メンバー削除             |

### メッセージ

| Method | Path                            | 説明                  |
|--------|---------------------------------|-----------------------|
| GET    | /api/channels/{id}/messages     | メッセージ一覧（ページネーション） |
| POST   | /api/channels/{id}/messages     | メッセージ送信         |
| DELETE | /api/messages/{id}              | メッセージ削除         |
| GET    | /api/messages/{id}/thread       | スレッド取得           |
| POST   | /api/messages/{id}/thread       | スレッド返信           |
| GET    | /api/messages/search?q=keyword  | メッセージ検索         |

### DM

| Method | Path                                  | 説明                    |
|--------|---------------------------------------|-------------------------|
| GET    | /api/dm                               | DM 会話一覧             |
| POST   | /api/dm                               | DM 開始（相手ユーザー指定）|
| GET    | /api/dm/{conversation_id}/messages    | DM メッセージ一覧        |

### ファイル

| Method | Path             | 説明              |
|--------|------------------|-------------------|
| POST   | /api/files/upload | ファイルアップロード |

## Socket.IO イベント

| イベント       | 方向           | 説明                         |
|--------------|----------------|------------------------------|
| connect      | client → server | 接続（JWT 検証）              |
| join_channel | client → server | チャンネルルーム参加           |
| leave_channel| client → server | チャンネルルーム退出           |
| new_message  | bidirectional   | メッセージ送受信               |
| typing       | bidirectional   | タイピングインジケーター        |
| user_online  | server → client | ユーザーがオンラインになった通知  |
| user_offline | server → client | ユーザーがオフラインになった通知  |

## 設計上の決定事項

| 決定事項                | 内容                                       |
|------------------------|--------------------------------------------|
| DM の実装               | `is_private=True` + `members=[A, B]` のチャンネルとして表現。専用コレクション不要 |
| ファイルストレージ（MVP） | `backend/uploads/` にローカル保存。将来 S3 互換ストレージへ差し替え可能な抽象化レイヤーを設ける |
| 状態管理               | Zustand（Redux より軽量、Socket.IO 統合がシンプル）|
| MongoDB 検索           | MongoDB ネイティブテキストインデックス（MVP）。全文検索エンジンは将来対応 |
| Redis（スケーリング）   | MVP では不要。単一プロセス運用。将来 Socket.IO Adapter として追加 |
| コンテナ化             | MongoDB のみ Docker Compose でコンテナ化。アプリは Dev Container 内で直接実行 |
