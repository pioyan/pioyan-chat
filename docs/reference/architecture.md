# システムアーキテクチャ

pioyan-chat のシステム全体の構成と技術スタックを説明します。

## 技術スタック

| レイヤー | 技術 | 補足 |
|---------|------|------|
| フロントエンド | Next.js 15 (React) + TypeScript | App Router, Tailwind CSS |
| バックエンド | Python + FastAPI | uvicorn ASGI サーバー |
| リアルタイム通信 | Socket.IO | python-socketio + socket.io-client |
| データベース | MongoDB 7 | Motor（非同期ドライバ） |
| 認証 | JWT | python-jose + passlib |
| 状態管理 | Zustand | フロントエンドグローバルストア |
| パッケージ管理 | pnpm (Node.js) / pip (Python) | |
| コンテナ | Docker Compose | MongoDB のみコンテナ化 |
| Linter / Formatter | ESLint + Prettier (TS) / Ruff (Python) | |
| テスト | Vitest + RTL (TS) / pytest (Python) | |

## システム構成図

```text
┌─────────────────────────────────────────────────────────┐
│                  ブラウザ (Next.js 15)                   │
│                                                         │
│  Sidebar ──→ ChatStore (Zustand) ←── useSocket          │
│     │              │                      │             │
│  MessageList    lib/api.ts          lib/socket.ts       │
│  MessageInput   (fetch)             (Socket.IO Client)  │
│  ThreadPanel    lib/auth.ts                             │
│  SearchModal                                            │
└───────────────┬──────────────────────────┬──────────────┘
                │ HTTP (REST API)          │ WebSocket
                ▼                          ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI + Socket.IO                     │
│                                                         │
│  routers/auth.py       ─→ app/auth/utils.py             │
│  routers/channels.py   ─→ app/auth/dependencies.py      │
│  routers/messages.py   ─→ app/database.py               │
│  routers/dm.py             │                            │
│  routers/files.py          │                            │
│  routers/bots.py           │                            │
│  sockets.py (Socket.IO) ───┘                            │
└───────────────────────────┬─────────────────────────────┘
                            │ Motor (非同期)
                            ▼
                    ┌───────────────┐
                    │  MongoDB 7    │
                    │  (Docker)     │
                    └───────────────┘
```

## ディレクトリ構成

```text
pioyan-chat/
├── frontend/                    # Next.js 15 (React) アプリ
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/          #   ログイン・サインアップ画面
│   │   │   └── (chat)/          #   チャット本体（3 カラムレイアウト）
│   │   ├── components/          #   再利用可能な UI コンポーネント
│   │   ├── hooks/               #   カスタム React フック
│   │   ├── lib/                 #   ユーティリティ (API / Auth / Socket)
│   │   ├── stores/              #   Zustand ストア
│   │   └── types/               #   共有型定義
│   ├── package.json
│   └── vitest.config.ts
├── backend/                     # FastAPI アプリ
│   ├── app/
│   │   ├── main.py              #   エントリポイント
│   │   ├── config.py            #   環境変数設定
│   │   ├── database.py          #   MongoDB 接続管理
│   │   ├── auth/                #   JWT・パスワード認証
│   │   ├── models/              #   Pydantic モデル
│   │   ├── routers/             #   FastAPI ルーター
│   │   ├── bots/                #   ボットバリデーター
│   │   └── sockets.py           #   Socket.IO イベントハンドラ
│   ├── tests/                   #   pytest テスト
│   ├── uploads/                 #   アップロードファイル
│   └── pyproject.toml
├── docker-compose.yml           # MongoDB 7 + mongo-express
├── docs/                        # システムドキュメント（本ディレクトリ）
│   ├── guides/                  #   開発・利用ガイド
│   ├── reference/               #   技術リファレンス
│   └── reports/                 #   検証・ステータスレポート
├── PLAN.md                      # 構築計画・チェックリスト
└── README.md                    # プロジェクト README
```

## 機能スコープ（MVP）

| 機能 | 優先度 | 状態 |
|------|--------|------|
| ユーザー認証（サインアップ / ログイン） | Must | ✅ |
| チャンネル（パブリック / プライベート） | Must | ✅ |
| リアルタイムメッセージ送受信 | Must | ✅ |
| ダイレクトメッセージ（DM） | Must | ✅ |
| ファイルアップロード・画像共有 | Should | ✅ |
| メッセージ検索 | Should | ✅ |
| スレッド（返信） | Should | ✅ |
| オンラインステータス表示 | Should | ✅ |
| タイピングインジケーター | Could | ✅ |

## 設計上の決定事項

| 決定事項 | 内容 |
|---------|------|
| DM の実装 | `is_direct=True` + `members=[A, B]` のチャンネルとして表現。専用コレクション不要 |
| スレッドの実装 | `thread_id` を持つ Message として表現。専用コレクション不要 |
| ファイルストレージ（MVP） | `backend/uploads/` にローカル保存。将来 S3 互換ストレージへ差し替え可能 |
| 状態管理 | Zustand（Redux より軽量、Socket.IO 統合がシンプル） |
| MongoDB 検索 | MongoDB ネイティブテキストインデックス（MVP）。全文検索エンジンは将来対応 |
| Redis（スケーリング） | MVP では不要。単一プロセス運用。将来 Socket.IO Adapter として追加 |
| コンテナ化 | MongoDB のみ Docker Compose でコンテナ化。アプリは Dev Container 内で直接実行 |
| ボットコンテナ | Dockerfile をアップロード・バリデーション後に保存。将来 Docker Build + Copilot SDK 統合 |
