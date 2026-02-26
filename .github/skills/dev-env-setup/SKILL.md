---
name: dev-env-setup
description: "ユーザーの要件に基づいて Dev Container・CI・Dependabot・VS Code 設定等の開発環境を構築するスキル。言語別テンプレートとヒアリングガイドを提供します。開発環境のセットアップを行うときに使用してください。"
---

# 開発環境セットアップスキル

## 概要

ユーザーが指定したプログラミング言語・フレームワーク・要件に基づいて、
プロジェクトの開発環境を一括で構築するための手順とテンプレートを提供します。

既存スキル `/ci-hygiene` と `/dependabot-baseline` を補完し、
言語固有の設定に特化した手順を定義します。

## ヒアリングテンプレート

環境構築を開始する前に、以下の情報をユーザーに確認してください:

```text
🛠️ 開発環境セットアップ — ヒアリング

【必須】
1. プログラミング言語: (例: Node.js / Python / Go / Rust / Java)
2. 言語バージョン: (例: Node.js 22 / Python 3.13)
3. パッケージマネージャ: (例: npm / yarn / pnpm / pip / poetry)

【任意（スキップ可）】
4. フレームワーク: (例: Next.js / FastAPI / Gin)
5. データベース: (例: PostgreSQL / MySQL / Redis)
6. キャッシュ・その他サービス: (例: Redis / RabbitMQ)
7. テストフレームワーク: (例: Jest / Vitest / pytest)
8. リンター・フォーマッター: (例: ESLint / Prettier / Ruff)
9. その他の要件: (自由記述)
```

## 言語別テンプレート

### Node.js

#### Dev Container

```jsonc
{
  "name": "<project-name>",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:<version>",
  // ── Features ──
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {}
  },
  // ── 初回セットアップ ──
  "postCreateCommand": "npm ci && echo '✅ Dev Container ready.'",
  // ── VS Code カスタマイズ ──
  "customizations": {
    "vscode": {
      "extensions": [
        "GitHub.copilot-chat",
        "GitHub.vscode-github-actions",
        "GitHub.vscode-pull-request-github",
        "DavidAnson.vscode-markdownlint",
        "redhat.vscode-yaml",
        "streetsidesoftware.code-spell-checker",
        "EditorConfig.EditorConfig",
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode"
      ],
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash",
        "editor.defaultFormatter": "esbenp.prettier-vscode",
        "editor.formatOnSave": true
      }
    }
  }
}
```

#### パッケージマネージャ別の postCreateCommand

| マネージャ | コマンド |
|-----------|---------|
| npm | `npm ci` |
| yarn | `corepack enable && yarn install --immutable` |
| pnpm | `corepack enable && pnpm install --frozen-lockfile` |

#### CI ジョブ（言語固有部分）

```yaml
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: ['20', '22']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run build --if-present
```

#### Dependabot 追加設定

```yaml
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Asia/Tokyo"
    commit-message:
      prefix: "deps"
    labels:
      - "dependencies"
```

#### VS Code 拡張機能

| 拡張 ID | 用途 |
|---------|------|
| `dbaeumer.vscode-eslint` | ESLint 統合 |
| `esbenp.prettier-vscode` | Prettier フォーマッター |
| `bradlc.vscode-tailwindcss` | Tailwind CSS（使用時のみ） |
| `yoavbls.pretty-ts-errors` | TypeScript エラー表示改善 |

---

### Python

#### Dev Container

```jsonc
{
  "name": "<project-name>",
  "image": "mcr.microsoft.com/devcontainers/python:<version>",
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {}
  },
  "postCreateCommand": "pip install -e '.[dev]' && echo '✅ Dev Container ready.'",
  "customizations": {
    "vscode": {
      "extensions": [
        "GitHub.copilot-chat",
        "GitHub.vscode-github-actions",
        "GitHub.vscode-pull-request-github",
        "DavidAnson.vscode-markdownlint",
        "redhat.vscode-yaml",
        "streetsidesoftware.code-spell-checker",
        "EditorConfig.EditorConfig",
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff"
      ],
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash",
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "[python]": {
          "editor.defaultFormatter": "charliermarsh.ruff",
          "editor.formatOnSave": true
        }
      }
    }
  }
}
```

#### パッケージマネージャ別の postCreateCommand

| マネージャ | コマンド |
|-----------|---------|
| pip | `pip install -e '.[dev]'` |
| poetry | `pip install poetry && poetry install` |
| pipenv | `pip install pipenv && pipenv install --dev` |
| uv | `pip install uv && uv sync` |

#### CI ジョブ（言語固有部分）

```yaml
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.12', '3.13']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e '.[dev]'
      - run: pytest --tb=short
```

#### Dependabot 追加設定

```yaml
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Asia/Tokyo"
    commit-message:
      prefix: "deps"
    labels:
      - "dependencies"
```

#### VS Code 拡張機能

| 拡張 ID | 用途 |
|---------|------|
| `ms-python.python` | Python 言語サポート |
| `ms-python.vscode-pylance` | 型チェック・IntelliSense |
| `charliermarsh.ruff` | Ruff リンター・フォーマッター |
| `ms-python.debugpy` | デバッガー |

---

### Go

#### Dev Container

```jsonc
{
  "name": "<project-name>",
  "image": "mcr.microsoft.com/devcontainers/go:<version>",
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {}
  },
  "postCreateCommand": "go mod download && echo '✅ Dev Container ready.'",
  "customizations": {
    "vscode": {
      "extensions": [
        "GitHub.copilot-chat",
        "GitHub.vscode-github-actions",
        "GitHub.vscode-pull-request-github",
        "DavidAnson.vscode-markdownlint",
        "redhat.vscode-yaml",
        "streetsidesoftware.code-spell-checker",
        "EditorConfig.EditorConfig",
        "golang.go"
      ],
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash",
        "go.lintTool": "golangci-lint",
        "go.lintFlags": ["--fast"],
        "[go]": {
          "editor.defaultFormatter": "golang.go",
          "editor.formatOnSave": true
        }
      }
    }
  }
}
```

#### CI ジョブ（言語固有部分）

```yaml
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: 'go.mod'
      - run: go test ./...
      - run: go vet ./...

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: 'go.mod'
      - uses: golangci/golangci-lint-action@v6
```

#### Dependabot 追加設定

```yaml
  - package-ecosystem: "gomod"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Asia/Tokyo"
    commit-message:
      prefix: "deps"
    labels:
      - "dependencies"
```

#### VS Code 拡張機能

| 拡張 ID | 用途 |
|---------|------|
| `golang.go` | Go 言語サポート（デバッグ・テスト・lint 統合） |

---

### Rust

#### Dev Container

```jsonc
{
  "name": "<project-name>",
  "image": "mcr.microsoft.com/devcontainers/rust:latest",
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {}
  },
  "postCreateCommand": "cargo build && echo '✅ Dev Container ready.'",
  "customizations": {
    "vscode": {
      "extensions": [
        "GitHub.copilot-chat",
        "GitHub.vscode-github-actions",
        "GitHub.vscode-pull-request-github",
        "DavidAnson.vscode-markdownlint",
        "redhat.vscode-yaml",
        "streetsidesoftware.code-spell-checker",
        "EditorConfig.EditorConfig",
        "rust-lang.rust-analyzer",
        "tamasfe.even-better-toml"
      ],
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash",
        "[rust]": {
          "editor.defaultFormatter": "rust-lang.rust-analyzer",
          "editor.formatOnSave": true
        }
      }
    }
  }
}
```

#### CI ジョブ（言語固有部分）

```yaml
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo test
      - run: cargo clippy -- -D warnings
      - run: cargo fmt -- --check
```

#### Dependabot 追加設定

```yaml
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Asia/Tokyo"
    commit-message:
      prefix: "deps"
    labels:
      - "dependencies"
```

#### VS Code 拡張機能

| 拡張 ID | 用途 |
|---------|------|
| `rust-lang.rust-analyzer` | Rust 言語サポート |
| `tamasfe.even-better-toml` | TOML 構文サポート |

---

### Java

#### Dev Container

```jsonc
{
  "name": "<project-name>",
  "image": "mcr.microsoft.com/devcontainers/java:<version>",
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers/features/docker-outside-of-docker:1": {},
    "ghcr.io/devcontainers/features/java:1": {
      "installMaven": true,
      "installGradle": false
    }
  },
  "postCreateCommand": "mvn dependency:resolve && echo '✅ Dev Container ready.'",
  "customizations": {
    "vscode": {
      "extensions": [
        "GitHub.copilot-chat",
        "GitHub.vscode-github-actions",
        "GitHub.vscode-pull-request-github",
        "DavidAnson.vscode-markdownlint",
        "redhat.vscode-yaml",
        "streetsidesoftware.code-spell-checker",
        "EditorConfig.EditorConfig",
        "vscjava.vscode-java-pack",
        "vmware.vscode-spring-boot"
      ],
      "settings": {
        "terminal.integrated.defaultProfile.linux": "bash",
        "java.format.settings.url": "",
        "java.saveActions.organizeImports": true
      }
    }
  }
}
```

#### ビルドツール別の postCreateCommand

| ツール | コマンド |
|--------|---------|
| Maven | `mvn dependency:resolve` |
| Gradle | `gradle dependencies` |

#### CI ジョブ（言語固有部分）

```yaml
  # Maven の場合
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '21'
          cache: 'maven'
      - run: mvn verify --batch-mode
```

```yaml
  # Gradle の場合
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '21'
      - uses: gradle/actions/setup-gradle@v4
      - run: gradle test
```

#### Dependabot 追加設定

```yaml
  # Maven
  - package-ecosystem: "maven"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Asia/Tokyo"
    commit-message:
      prefix: "deps"
    labels:
      - "dependencies"
```

```yaml
  # Gradle
  - package-ecosystem: "gradle"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Asia/Tokyo"
    commit-message:
      prefix: "deps"
    labels:
      - "dependencies"
```

#### VS Code 拡張機能

| 拡張 ID | 用途 |
|---------|------|
| `vscjava.vscode-java-pack` | Java 拡張パック（言語サポート・デバッグ・テスト・Maven） |
| `vmware.vscode-spring-boot` | Spring Boot サポート（使用時のみ） |

---

## Docker Compose テンプレート（DB・サービス）

データベースやキャッシュが必要な場合、`docker-compose.yml` を作成し、
`devcontainer.json` の `dockerComposeFile` で参照します。

### devcontainer.json（Compose 連携時）

```jsonc
{
  "name": "<project-name>",
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspaces/${localWorkspaceFolderBasename}",
  // ... customizations は同様
}
```

### PostgreSQL

```yaml
services:
  app:
    image: mcr.microsoft.com/devcontainers/<language>:<version>
    volumes:
      - ../..:/workspaces:cached
    command: sleep infinity
    depends_on:
      - db

  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpass
      POSTGRES_DB: devdb
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

### MySQL

```yaml
services:
  app:
    image: mcr.microsoft.com/devcontainers/<language>:<version>
    volumes:
      - ../..:/workspaces:cached
    command: sleep infinity
    depends_on:
      - db

  db:
    image: mysql:8.4
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: devdb
      MYSQL_USER: devuser
      MYSQL_PASSWORD: devpass
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql

volumes:
  mysql-data:
```

### Redis

```yaml
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
```

## Copilot Hooks 更新ガイド

`.vscode/settings.json` の `github.copilot.chat.codeGeneration.instructions` や
Copilot Hooks に言語固有のチェックを追加する際の参考:

### postSave フック追加例

```jsonc
{
  "github.copilot.chat.commandHooks": {
    "postSave": [
      // 既存のフック...
      {
        "pattern": "**/*.{ts,tsx,js,jsx}",
        "command": "npx eslint --fix ${file}"
      },
      {
        "pattern": "**/*.py",
        "command": "ruff check --fix ${file}"
      },
      {
        "pattern": "**/*.go",
        "command": "gofmt -w ${file}"
      }
    ]
  }
}
```

## 関連スキル

- `/ci-hygiene` — 言語非依存の衛生チェック CI の導入手順
- `/dependabot-baseline` — Dependabot の最小構成と段階拡大の手順

言語固有の CI ジョブは、衛生チェック CI と**別ジョブ**として追加してください。
衛生チェックの既存ジョブを変更しないこと。

