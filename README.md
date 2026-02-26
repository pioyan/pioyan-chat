# pioyan-chat

Slack / RocketChat ライクなリアルタイムチャットアプリケーション MVP。
Next.js + FastAPI + Socket.IO + MongoDB で構築されています。

## 概要

pioyan-chat は pioyan が開発するリアルタイムチャットアプリです。
チャンネル・DM・スレッド・ファイル共有・メッセージ検索に対応しています。

## セットアップ

### 前提条件

- [VS Code](https://code.visualstudio.com/) + [Dev Containers 拡張](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker](https://www.docker.com/)

### Dev Container で開始（推奨）

```bash
git clone https://github.com/pioyan/pioyan-chat.git
cd pioyan-chat
```

1. VS Code でフォルダを開く
2. コマンドパレット → **Dev Containers: Reopen in Container** を実行
3. コンテナが起動したら、ターミナルで GitHub CLI を認証:

```bash
gh auth login
```

> **Note**: 推奨拡張機能はコンテナ起動時に自動インストールされます。

### ローカル開発（Dev Container を使わない場合）

**前提**: Node.js 22+、Python 3.12+、Docker が必要です。

```bash
git clone https://github.com/pioyan/pioyan-chat.git
cd pioyan-chat
# フロントエンド依存インストール
corepack enable && cd frontend && pnpm install
# バックエンド依存インストール
cd ../backend && pip install -e '.[dev]'
```

### 開発サーバー起動

**1. MongoDB を起動:**

```bash
docker compose up -d
```

**2. バックエンドを起動:**

```bash
cd backend
cp ../.env.example .env  # 初回のみ
python -m uvicorn app.main:socket_app --reload --port 8000
```

**3. フロントエンドを起動:**

```bash
cd frontend
pnpm dev
```

ブラウザで <http://localhost:3000> を開いてください。

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| フロントエンド | Next.js 15 (React) + TypeScript + Tailwind CSS |
| バックエンド | Python + FastAPI + python-socketio |
| リアルタイム通信 | Socket.IO |
| データベース | MongoDB 7 (Motor 非同期ドライバ) |
| 認証 | JWT (python-jose + passlib) |
| 状態管理 | Zustand |
| テスト | Vitest + React Testing Library / pytest |

## テスト

```bash
# バックエンド（MongoDB が起動していること）
cd backend && pytest

# フロントエンド
cd frontend && pnpm test
```

## AI コーディング環境

このリポジトリは GitHub Copilot を活用した AI コーディングに最適化されています。

### Copilot Hooks

コード生成・編集後に品質チェックが自動実行されます（`.vscode/settings.json` で設定）:

| フック | 対象 | 実行コマンド |
|--------|------|------------|
| postSave | `*.md` | markdownlint |
| postSave | `*.yml` / `*.yaml` | yamllint |
| postSave | `*.py` | ruff check --fix |
| postSave | `frontend/**/*.{ts,tsx}` | eslint --fix |
| postCommand | 全ファイル | typos |

### カスタムエージェント

Copilot Chat から以下のエージェントを呼び出せます:

| エージェント | 用途 |
|------------|------|
| `@feature-builder` | TDD サイクルで機能を実装 |
| `@repo-guardian` | リポジトリ標準化の監査・適用 |
| `@code-reviewer` | PR レビューコメントの提案 |
| `@docs-writer` | ドキュメント更新提案の生成 |
| `@git-operator` | ブランチ・コミット・PR 運用 |

### Agent Skills

| スキル | 内容 |
|--------|------|
| `/repo-audit` | ベストプラクティス準拠の監査 |
| `/repo-apply-baseline` | 不足ファイルの追加 |
| `/ci-hygiene` | CI 衛生チェックの導入 |
| `/dependabot-baseline` | Dependabot の最小構成導入 |
| `/git-workflow` | Git 運用の標準手順 |

## API エンドポイント

| Method | Path | 説明 |
|--------|------|------|
| POST | /api/auth/signup | 新規登録 |
| POST | /api/auth/login | ログイン（JWT 発行） |
| GET | /api/channels | チャンネル一覧 |
| POST | /api/channels | チャンネル作成 |
| GET | /api/channels/{id}/messages | メッセージ一覧 |
| POST | /api/channels/{id}/messages | メッセージ送信 |
| GET | /api/dm | DM 会話一覧 |
| POST | /api/files/upload | ファイルアップロード |

詳細は [PLAN.md](PLAN.md) を参照してください。

## 開発に参加する

開発への参加方法は [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## セキュリティ

脆弱性の報告方法は [SECURITY.md](SECURITY.md) をご覧ください。

## ライセンス

このプロジェクトは [MIT License](LICENSE) の下で公開されています。
