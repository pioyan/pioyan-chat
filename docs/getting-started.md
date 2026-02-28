# セットアップガイド

pioyan-chat の開発環境をセットアップし、ローカルで動作させるまでの手順です。

## 前提条件

- [VS Code](https://code.visualstudio.com/) + [Dev Containers 拡張](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker](https://www.docker.com/)
- [GitHub CLI](https://cli.github.com/)（推奨）

## Dev Container で開始（推奨）

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

> 推奨拡張機能はコンテナ起動時に自動インストールされます。

### Dev Container に含まれる環境

| ツール | バージョン | 用途 |
|--------|-----------|------|
| Node.js | 22 | フロントエンド開発（pnpm 対応） |
| Python | 3.13 | バックエンド開発 |
| Docker CLI | — | MongoDB コンテナの実行 |
| GitHub CLI | — | PR・Issue 操作 |

## ローカル開発（Dev Container を使わない場合）

**前提**: Node.js 22+、Python 3.12+、Docker が必要です。

```bash
git clone https://github.com/pioyan/pioyan-chat.git
cd pioyan-chat

# フロントエンド依存インストール
corepack enable && cd frontend && pnpm install

# バックエンド依存インストール
cd ../backend && pip install -e '.[dev]'
```

## 開発サーバー起動

### 1. MongoDB を起動

```bash
docker compose up -d
```

`mongo-express` の管理 UI: <http://localhost:8081>

### 2. バックエンドを起動

```bash
cd backend
cp ../.env.example .env  # 初回のみ
python -m uvicorn app.main:socket_app --reload --port 8000
```

API ドキュメント（Swagger UI）: <http://localhost:8000/docs>

### 3. フロントエンドを起動

```bash
cd frontend
pnpm dev
```

ブラウザで <http://localhost:3000> を開いてください。

## 動作確認

```bash
# バックエンドのヘルスチェック
curl http://localhost:8000/health
# => {"status": "ok"}

# フロントエンドの起動確認
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
# => 200
```

## 停止

```bash
# MongoDB + mongo-express を停止
docker compose down

# ボリュームも削除する場合
docker compose down -v
```
