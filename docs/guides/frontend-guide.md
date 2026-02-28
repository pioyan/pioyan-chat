# フロントエンドガイド

Next.js 15（React + TypeScript + Tailwind CSS）で構築されたフロントエンドの設計と構成。

## ディレクトリ構成

```text
frontend/src/
├── app/
│   ├── globals.css          # Tailwind CSS グローバルスタイル
│   ├── layout.tsx           # ルートレイアウト
│   ├── (auth)/              # 認証ページ（ログイン・サインアップ）
│   └── (chat)/              # チャット本体（3 カラムレイアウト）
├── components/
│   ├── Sidebar.tsx           # チャンネル・DM リスト（左カラム）
│   ├── MessageList.tsx       # メッセージ一覧（中央カラム）
│   ├── MessageInput.tsx      # メッセージ入力・ファイル添付
│   ├── MessageItem.tsx       # メッセージ単体（スレッド数・ファイルアイコン）
│   ├── ThreadPanel.tsx       # スレッドビュー（右サイドパネル）
│   ├── SearchModal.tsx       # メッセージ全文検索モーダル
│   ├── CreateChannelModal.tsx # チャンネル作成モーダル
│   ├── ProfileModal.tsx      # プロフィール編集モーダル
│   └── MarkdownContent.tsx   # Markdown レンダリング
├── hooks/
│   └── useSocket.ts          # Socket.IO イベント購読フック
├── lib/
│   ├── api.ts                # API クライアント（fetch ベース）
│   ├── auth.ts               # JWT トークン管理
│   └── socket.ts             # Socket.IO クライアントシングルトン
├── stores/
│   └── chatStore.ts          # Zustand グローバルストア
├── types/
│   └── index.ts              # 共有型定義
├── proxy.ts                  # Next.js Middleware（認証リダイレクト）
└── test/                     # Vitest テスト
```

## UI レイアウト

Slack 風の 3 カラムデザインです。

```text
┌──────────┬─────────────────────┬──────────────┐
│          │                     │              │
│ Sidebar  │    MessageList      │ ThreadPanel  │
│          │                     │  (条件表示)   │
│ channels │    MessageItem...   │              │
│ DMs      │                     │              │
│          │    MessageInput     │              │
│          │                     │              │
└──────────┴─────────────────────┴──────────────┘
```

## コンポーネント詳細

### Sidebar

- パブリック / プライベートチャンネルの一覧表示
- DM 会話の一覧表示
- チャンネル作成ボタン
- ログアウトボタン

### MessageList / MessageItem

- ページネーション付きメッセージ取得（`before` パラメータ）
- スレッド返信数の表示
- ファイル添付の表示（画像はインラインプレビュー）
- 送信者アバター・ユーザー名

### MessageInput

- テキスト入力
- ファイル添付（`/api/files/upload` 経由でアップロード後に URL を送信）
- タイピングインジケーター送信

### ThreadPanel

- 親メッセージの表示
- スレッド返信一覧
- 返信入力

### SearchModal

- メッセージ全文検索（`/api/messages/search?q=` を利用）

## 状態管理（Zustand）

`stores/chatStore.ts` でグローバル状態を管理します。

主な状態:

| 状態 | 型 | 説明 |
|------|-----|------|
| `channels` | `Channel[]` | チャンネル一覧 |
| `currentChannel` | `Channel \| null` | 選択中のチャンネル |
| `messages` | `Message[]` | 現在のチャンネルのメッセージ |
| `user` | `User \| null` | ログインユーザー |

## API クライアント（`lib/api.ts`）

`fetch` ベースの型付き API クライアントです。

```typescript
// 使用例
import { authApi, channelsApi, messagesApi } from "@/lib/api";

// ログイン
const { access_token } = await authApi.login({ email, password });

// チャンネル一覧
const channels = await channelsApi.list();

// メッセージ送信
const msg = await messagesApi.post(channelId, { content: "Hello!" });
```

提供されるクライアント:

| モジュール | エンドポイント |
|-----------|--------------|
| `authApi` | `/api/auth/*` |
| `channelsApi` | `/api/channels/*` |
| `messagesApi` | `/api/channels/{id}/messages`, `/api/messages/*` |
| `dmApi` | `/api/dm/*` |
| `filesApi` | `/api/files/*` |
| `botsApi` | `/api/bots/*` |

## JWT 管理（`lib/auth.ts`）

- `localStorage` にトークンを保存
- Cookie にも同期（Next.js Middleware で認証チェックに利用）
- 有効期限: 7 日間

```typescript
import { saveToken, getToken, removeToken, isAuthenticated } from "@/lib/auth";
```

## Socket.IO クライアント（`lib/socket.ts`）

シングルトンパターンで Socket.IO クライアントを管理します。

```typescript
import {
  connectSocket,
  disconnectSocket,
  joinChannel,
  leaveChannel,
  sendMessage,
  emitTyping,
} from "@/lib/socket";
```

接続時に JWT トークンを `auth.token` として送信します。

## テスト

Vitest + React Testing Library を使用。

```bash
cd frontend
pnpm test          # run モード
pnpm test:watch    # watch モード
```
