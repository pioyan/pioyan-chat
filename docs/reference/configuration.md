# 環境設定リファレンス

pioyan-chat の環境変数・Docker Compose・その他設定項目をまとめています。

## 環境変数

バックエンドは `pydantic-settings` で環境変数を管理します。  
`.env` ファイルまたは環境変数から読み込まれます。

### バックエンド設定（`backend/app/config.py`）

| 環境変数 | デフォルト | 説明 |
|---------|----------|------|
| `MONGO_URL` | `mongodb://admin:password@localhost:27017/pioyan_chat?authSource=admin` | MongoDB 接続 URI |
| `MONGO_DB` | `pioyan_chat` | データベース名 |
| `JWT_SECRET` | `change-me-to-a-random-secret-at-least-32-chars` | JWT 署名キー（**本番では必ず変更**） |
| `JWT_ALGORITHM` | `HS256` | JWT 署名アルゴリズム |
| `JWT_EXPIRE_MINUTES` | `10080`（7日） | JWT トークン有効期限（分） |
| `BACKEND_PORT` | `8000` | バックエンドポート |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | CORS 許可オリジン |
| `UPLOAD_DIR` | `uploads` | ファイルアップロード保存先ディレクトリ |
| `MAX_FILE_SIZE_MB` | `10` | ファイルアップロード最大サイズ（MB） |
| `CONTAINER_FILES_DIR` | `container_files` | ボット用コンテナファイル保存先 |
| `MAX_CONTAINER_FILE_SIZE_KB` | `256` | コンテナファイル最大サイズ（KB） |

### フロントエンド設定

| 環境変数 | デフォルト | 説明 |
|---------|----------|------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | バックエンド API の URL |
| `NEXT_PUBLIC_SOCKET_URL` | `http://localhost:8000` | Socket.IO サーバーの URL |

### `.env.example`

初回セットアップ時にコピーして使用します:

```bash
cd backend
cp ../.env.example .env
```

## Docker Compose

`docker-compose.yml` で以下のサービスが定義されています。

### MongoDB

```yaml
mongodb:
  image: mongo:7
  ports:
    - "27017:27017"
  environment:
    MONGO_INITDB_ROOT_USERNAME: ${MONGO_USERNAME:-admin}
    MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD:-password}
    MONGO_INITDB_DATABASE: ${MONGO_DB:-pioyan_chat}
  volumes:
    - mongodb_data:/data/db
```

### mongo-express（管理 UI）

```yaml
mongo-express:
  image: mongo-express:1
  ports:
    - "8081:8081"
  environment:
    ME_CONFIG_BASICAUTH: false
```

管理 UI: <http://localhost:8081>

### Docker Compose 環境変数

| 変数 | デフォルト | 説明 |
|------|----------|------|
| `MONGO_USERNAME` | `admin` | MongoDB root ユーザー名 |
| `MONGO_PASSWORD` | `password` | MongoDB root パスワード |
| `MONGO_DB` | `pioyan_chat` | 初期データベース名 |

### 操作コマンド

```bash
# 起動
docker compose up -d

# 停止
docker compose down

# 停止 + データ削除
docker compose down -v

# ログ確認
docker compose logs -f mongodb
```

## ポート一覧

| サービス | ポート | 用途 |
|---------|--------|------|
| フロントエンド (Next.js) | 3000 | Web UI |
| バックエンド (FastAPI) | 8000 | REST API + Socket.IO |
| MongoDB | 27017 | データベース |
| mongo-express | 8081 | MongoDB 管理 UI |

## Copilot Hooks（`.vscode/settings.json`）

ファイル保存時に自動実行されるフック:

| フック | 対象 | 実行コマンド |
|--------|------|------------|
| postSave | `*.md` | markdownlint |
| postSave | `*.yml` / `*.yaml` | yamllint |
| postSave | `*.py` | `ruff check --fix` |
| postSave | `frontend/**/*.{ts,tsx}` | `eslint --fix` |
| postCommand | 全ファイル | `typos` |
