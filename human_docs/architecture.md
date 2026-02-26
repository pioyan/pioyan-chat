# アーキテクチャ概要

pioyan-chat リポジトリの構成と各ファイルの役割を説明します。

## ディレクトリ構造

```text
pioyan-chat/
├── frontend/                    # Next.js 15 (React) アプリ
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/          #   ログイン・サインアップ画面
│   │   │   └── (chat)/          #   チャット本体
│   │   ├── components/          #   再利用可能な UI コンポーネント
│   │   │   ├── MessageItem.tsx  #     メッセージ単体
│   │   │   ├── MessageList.tsx  #     メッセージ一覧
│   │   │   ├── MessageInput.tsx #     メッセージ入力欄
│   │   │   ├── Sidebar.tsx      #     チャンネル・DM リスト
│   │   │   ├── ThreadPanel.tsx  #     スレッドビュー
│   │   │   └── SearchModal.tsx  #     メッセージ検索モーダル
│   │   ├── hooks/               #   カスタム React フック
│   │   │   └── useSocket.ts     #     Socket.IO フック
│   │   ├── lib/                 #   ユーティリティ
│   │   │   ├── auth.ts          #     JWT 管理
│   │   │   ├── api.ts           #     Axios ラッパー
│   │   │   └── socket.ts        #     Socket.IO クライアント
│   │   ├── stores/
│   │   │   └── chatStore.ts     #     Zustand ストア
│   │   └── types/
│   │       └── index.ts         #     共有型定義
│   ├── package.json
│   └── vitest.config.ts
├── backend/                     # FastAPI アプリ
│   ├── app/
│   │   ├── main.py              #   エントリポイント (FastAPI + Socket.IO)
│   │   ├── config.py            #   環境変数設定 (pydantic-settings)
│   │   ├── database.py          #   MongoDB 接続管理 (Motor)
│   │   ├── auth/
│   │   │   ├── utils.py         #     JWT 生成・検証・パスワードハッシュ
│   │   │   └── dependencies.py  #     認証 FastAPI 依存関数
│   │   ├── models/
│   │   │   ├── user.py          #     User Pydantic モデル
│   │   │   ├── channel.py       #     Channel Pydantic モデル
│   │   │   └── message.py       #     Message Pydantic モデル
│   │   ├── routers/
│   │   │   ├── auth.py          #     signup / login / me
│   │   │   ├── channels.py      #     チャンネル CRUD + メンバー管理
│   │   │   ├── messages.py      #     メッセージ CRUD + 検索 + スレッド
│   │   │   ├── dm.py            #     ダイレクトメッセージ
│   │   │   └── files.py         #     ファイルアップロード
│   │   └── sockets.py           #   Socket.IO イベントハンドラ
│   ├── tests/                   #   pytest テスト
│   ├── uploads/                 #   アップロードファイル置き場（MVP）
│   └── pyproject.toml
├── docker-compose.yml           # MongoDB 7 サービス定義
├── .env.example                 # 環境変数テンプレート
├── .devcontainer/
│   └── devcontainer.json        # Dev Container 設定
├── .github/
│   ├── agents/                  # カスタムエージェント定義
│   ├── skills/                  # エージェントスキル（手順書）
│   ├── policies/                # 組織ポリシー文書
│   ├── workflows/
│   │   └── ci.yml               # GitHub Actions CI ワークフロー
│   ├── CODEOWNERS               # コードオーナー定義
│   ├── copilot-instructions.md  # Copilot カスタム指示
│   ├── dependabot.yml           # Dependabot 設定
│   └── PULL_REQUEST_TEMPLATE.md # PR テンプレート
├── .vscode/
│   ├── extensions.json          # 推奨 VS Code 拡張
│   ├── mcp.json                 # MCP サーバー設定
│   └── settings.json            # エディタ・Hooks 設定
├── human_docs/                  # 人間向けドキュメント（本ディレクトリ）
├── agent_docs/                  # AI エージェント向けリファレンス
├── PLAN.md                      # 構築計画・チェックリスト
├── CODE_OF_CONDUCT.md           # 行動規範
├── CONTRIBUTING.md              # 開発参加ガイド
├── LICENSE                      # MIT ライセンス
├── README.md                    # プロジェクト README
└── SECURITY.md                  # セキュリティポリシー
```

---

## システムアーキテクチャ

```text
┌─────────────────────────────────────────────────────────┐
│                  ブラウザ (Next.js 15)                   │
│                                                         │
│  Sidebar ──→ ChatStore (Zustand) ←── useSocket          │
│     │              │                      │             │
│  MessageList    lib/api.ts          lib/socket.ts       │
│  MessageInput   (Axios)             (Socket.IO Client)  │
│  ThreadPanel    lib/auth.ts                             │
│  SearchModal                                            │
└───────────────┬──────────────────────────┬──────────────┘
                │ HTTP (REST)              │ WebSocket
                ▼                          ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI + Socket.IO                     │
│                                                         │
│  routers/auth.py       ─→ app/auth/utils.py             │
│  routers/channels.py   ─→ app/auth/dependencies.py      │
│  routers/messages.py   ─→ app/database.py               │
│  routers/dm.py             │                            │
│  routers/files.py          │                            │
│  sockets.py (Socket.IO) ───┘                            │
└───────────────────────────┬─────────────────────────────┘
                            │ Motor (非同期)
                            ▼
                    ┌───────────────┐
                    │  MongoDB 7    │
                    │  (Docker)     │
                    └───────────────┘
```

---

## 各コンポーネントの詳細

### フロントエンド（`frontend/`）

| ファイル | 役割 |
|---------|------|
| `src/app/(auth)/` | ログイン・サインアップ画面 |
| `src/app/(chat)/` | チャット本体（3 カラムレイアウト） |
| `src/components/Sidebar.tsx` | チャンネル・DM リスト |
| `src/components/MessageList.tsx` | メッセージ一覧（ページネーション対応） |
| `src/components/MessageInput.tsx` | メッセージ入力・ファイル添付・スレッド返信 |
| `src/components/MessageItem.tsx` | メッセージ単体（スレッド数・ファイルアイコン） |
| `src/components/ThreadPanel.tsx` | スレッドビュー（右サイドパネル） |
| `src/components/SearchModal.tsx` | メッセージ全文検索モーダル |
| `src/lib/auth.ts` | JWT トークン管理（localStorage + リフレッシュ） |
| `src/lib/api.ts` | Axios インスタンス（Bearer トークン自動付与） |
| `src/lib/socket.ts` | Socket.IO クライアントシングルトン |
| `src/hooks/useSocket.ts` | Socket.IO イベント購読カスタムフック |
| `src/stores/chatStore.ts` | Zustand グローバルストア（channels / messages / DM） |
| `src/types/index.ts` | User / Channel / Message 共有型定義 |

### バックエンド（`backend/`）

| ファイル | 役割 |
|---------|------|
| `app/main.py` | FastAPI アプリ + Socket.IO 統合（`socket_app`） |
| `app/config.py` | pydantic-settings による環境変数管理 |
| `app/database.py` | Motor による MongoDB 接続管理・コレクションアクセサ |
| `app/auth/utils.py` | JWT 生成・検証（python-jose）・パスワードハッシュ（passlib） |
| `app/auth/dependencies.py` | `get_current_user` FastAPI 依存関数 |
| `app/models/user.py` | User Pydantic モデル（UserCreate / UserInDB / UserPublic） |
| `app/models/channel.py` | Channel Pydantic モデル（is_direct フラグで DM を表現） |
| `app/models/message.py` | Message Pydantic モデル（thread_id でスレッドを表現） |
| `app/routers/auth.py` | POST /signup, POST /login, GET /me |
| `app/routers/channels.py` | チャンネル CRUD + メンバー追加・削除 |
| `app/routers/messages.py` | メッセージ CRUD + 検索（テキストインデックス）+ スレッド |
| `app/routers/dm.py` | DM 会話一覧・開始・メッセージ取得 |
| `app/routers/files.py` | ファイルアップロード（`uploads/` へ保存） |
| `app/sockets.py` | Socket.IO イベント（join/leave/new_message/typing 等） |

### CI ワークフロー（`.github/workflows/ci.yml`）

| ジョブ | 対象 | 内容 |
|--------|------|------|
| `actionlint` | ワークフロー | GitHub Actions 静的解析 |
| `markdownlint` | `*.md` | Markdown 品質チェック |
| `yamllint` | `*.yml` | YAML 構文チェック |
| `gitleaks` | 全体 | シークレット漏洩検知 |
| `typos` | 全体 | 誤字検知 |
| `backend-lint` | `backend/` | Ruff lint + format check |
| `backend-test` | `backend/` | pytest（Python 3.12 / 3.13 matrix）|
| `frontend-lint` | `frontend/` | ESLint |
| `frontend-test` | `frontend/` | Vitest |
| `frontend-build` | `frontend/` | Next.js 本番ビルド検証 |

### データ設計

#### DM の実装方針

DM は専用コレクションを持たず、`is_direct=True` の Channel として実装しています:

```python
# Channel ドキュメントの例（DM）
{
  "_id": ObjectId("..."),
  "name": "dm_userA_userB",
  "is_direct": True,
  "members": ["userA_id", "userB_id"],
  "created_at": "..."
}
```

#### スレッドの実装方針

スレッドは `thread_id` を持つ Message として実装しています（専用コレクション不要）:

```python
# Message ドキュメントの例（スレッド返信）
{
  "_id": ObjectId("..."),
  "channel_id": "...",
  "thread_id": "parent_message_id",  # スレッド返信の場合
  "content": "返信内容",
  "user_id": "..."
}
```

#### MongoDB テキストインデックス（検索）

```python
# messages コレクションに作成
await db.messages.create_index([("content", "text")])
```

### Socket.IO イベント

| イベント | 方向 | 説明 |
|---------|------|------|
| `connect` | client → server | 接続（JWT 検証） |
| `join_channel` | client → server | チャンネルルーム参加 |
| `leave_channel` | client → server | チャンネルルーム退出 |
| `new_message` | bidirectional | メッセージ送受信 |
| `typing` | bidirectional | タイピングインジケーター |
| `user_online` | server → client | ユーザーオンライン通知 |
| `user_offline` | server → client | ユーザーオフライン通知 |

---

## 開発フロー

```text
1. PLAN.md でタスクを確認
      │
      ▼
2. feature ブランチ作成（/git-workflow を参照）
      │
      ▼
3. @feature-builder で TDD サイクルにより機能実装
      │  ├─ Red:   テストを先に書く（pytest / Vitest）
      │  ├─ Green: 実装してテストを通す
      │  └─ Refactor: コードを整理する
      │
      ▼
4. ローカルで確認
      │  ├─ cd backend && pytest
      │  ├─ cd frontend && pnpm test
      │  └─ cd frontend && pnpm build
      │
      ▼
5. @code-reviewer でセルフレビュー
      │
      ▼
6. PR 作成 → CI 全ジョブ通過 → マージ
```
