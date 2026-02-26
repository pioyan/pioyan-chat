# Copilot カスタム指示 — pioyan-chat

## プロジェクト概要

pioyan-chat は pioyan が開発する Slack 風リアルタイムチャットアプリケーションです。
詳細な構築計画は [PLAN.md](../PLAN.md) を参照してください。

## リポジトリ構成

```text
frontend/                # Next.js 15 (React + TypeScript + Tailwind CSS)
backend/                 # FastAPI + Socket.IO + Motor (async MongoDB)
docker-compose.yml       # MongoDB 7 サービス定義
.devcontainer/
└── devcontainer.json    # Dev Container 設定（Node.js 22・Python 3.13・gh CLI・推奨拡張）
.github/
├── agents/              # Custom Agents（Agent Builder・Repo Guardian・Code Reviewer・Docs Writer）
├── skills/              # Agent Skills（監査・適用・CI・Dependabot・Git ワークフロー）
├── policies/            # 組織ポリシー文書（チェックリスト・ツール一覧）
├── workflows/           # GitHub Actions CI
├── ISSUE_TEMPLATE/      # Issue テンプレート
├── CODEOWNERS           # コードオーナー
├── dependabot.yml       # 依存自動更新（Actions / npm / pip）
└── PULL_REQUEST_TEMPLATE.md
.vscode/
├── settings.json        # エージェント・Hooks 設定
├── extensions.json      # 推奨拡張機能
└── mcp.json             # ローカル MCP サーバー設定
agent_docs/              # AI エージェント向けリファレンス（自己参照用）
human_docs/              # 人間向けドキュメント
PLAN.md                  # チャットアプリ構築計画（フェーズ・API一覧・設計決定事項）
```

## コーディング規約

- コミットメッセージは Conventional Commits に従う
- ブランチ名は `<type>/<short-description>` 形式
- PR は必ずテンプレートに従い、CI を通過させてからレビューを依頼する
- アプリケーションコード（関数・クラス・モジュール）の新規作成・修正は TDD（t-wada 式 Red-Green-Refactor）で行う

## ビルド・テスト

### フロントエンド (Next.js)

```bash
cd frontend
pnpm dev          # 開発サーバー起動 (localhost:3000)
pnpm build        # 本番ビルド
pnpm test         # Vitest 単体テスト (run モード)
pnpm test:watch   # Vitest watch モード
pnpm lint         # ESLint
```

### バックエンド (FastAPI)

```bash
cd backend
python -m uvicorn app.main:socket_app --reload --port 8000   # 開発サーバー起動
pytest             # テスト実行
ruff check .       # lint
ruff format .      # フォーマット
```

### インフラ（Docker Compose）

```bash
docker compose up -d          # MongoDB + mongo-express 起動
docker compose down -v        # 停止・ボリューム削除
```

mongo-express の管理 UI: <http://localhost:8081>

## CI

PR を作成すると以下の衛生チェックが自動実行されます:

- **actionlint**: GitHub Actions の静的解析
- **markdownlint**: Markdown の品質チェック
- **yamllint**: YAML の構文チェック
- **gitleaks**: シークレット漏洩検知
- **typos**: 誤字検知
- **backend-lint**: Ruff（Python lint + format check）
- **backend-test**: pytest（Python 3.12 / 3.13 matrix、MongoDB サービスコンテナ付き）
- **frontend-lint**: ESLint（Next.js）
- **frontend-test**: Vitest
- **frontend-build**: Next.js 本番ビルド検証

## 開発環境

### Dev Container

`.devcontainer/devcontainer.json` で統一された開発環境を提供します:

- **ベースイメージ**: Microsoft Universal Image
- **Node.js 22**: pnpm 対応（corepack 経由）
- **Python 3.13**: pip 対応
- **GitHub CLI**: `gh` コマンドが利用可能（初回は `gh auth login` で認証）
- **Docker**: MongoDB 等のコンテナ実行に必要な Docker が利用可能
- **推奨拡張**: コンテナ起動時に自動インストール（ESLint, Prettier, ms-python, Ruff 等）
- **postCreateCommand**: pnpm install + pip install を自動実行

初回起動後は `docker compose up -d` で MongoDB を起動してください。

### Copilot Hooks

`.vscode/settings.json` で以下のフックが設定されています:

- **postSave**: `.md` → markdownlint、`.yml/.yaml` → yamllint、`.py` → ruff fix、`frontend/**/*.{ts,tsx}` → ESLint fix
- **postCommand**: コード変更後に typos チェックを自動実行

コード生成・編集のたびに品質チェックが自動で走るため、手動での lint 実行は不要です。

### サブエージェント連携

`chat.customAgentInSubagent.enabled: true` が有効化されており、
メインエージェントから以下のカスタムエージェントをサブエージェントとして呼び出すことができます。

## カスタムエージェント

このリポジトリには以下のカスタムエージェントが定義されています:

| エージェント | 用途 |
|------------|------|
| `@feature-builder` | pioyan-chat の機能を TDD サイクルで実装。Next.js / FastAPI 両対応。PLAN.md のチェックリストを追跡（本リポジトリ推奨） |
| `@agent-builder` | ユーザーの要件に応じたカスタムエージェントを対話的に設計・生成（コード実装エージェントには TDD サイクルを組み込み） |
| `@repo-guardian` | リポジトリのベストプラクティス準拠を監査し、不足分を PR で追加 |
| `@code-reviewer` | PR の差分をレビューし、品質・セキュリティ観点でコメントを提案 |
| `@docs-writer` | コード変更に伴うドキュメント更新提案を生成 |
| `@dev-env-builder` | ユーザーの要件に応じた開発環境（Dev Container・CI・Dependabot 等）を対話的に構築 |
| `@git-operator` | Git 運用に精通した専門エージェント。ブランチ・コミット・rebase・PR・Issue・hotfix/release を規約に沿って実行 |

## Agent Skills

このリポジトリには以下の Agent Skills が含まれています:

- `/repo-audit` — リポジトリのベストプラクティス準拠状況を監査
- `/repo-apply-baseline` — 不足ファイルを追加する
- `/ci-hygiene` — CI 衛生チェックの導入手順
- `/dependabot-baseline` — Dependabot の最小構成導入手順
- `/dev-env-setup` — 言語・フレームワークに応じた開発環境のセットアップ手順
- `/git-workflow` — Git 運用の標準手順（ブランチ・コミット・PR・rebase・hotfix・release）

Git の運用を指示された場合は、まず `/git-workflow` スキルを参照してください。

## エージェント向けリファレンス

`agent_docs/` には AI エージェントが自律的に参照するためのリファレンスがあります。
詳細な設計情報や連携ルールが必要な場合は、以下のファイルを `read_file` で取得してください。

- `agent_docs/reference-map.md` — エージェント・スキル・ポリシー間の依存関係マップ
- `agent_docs/design-patterns.md` — エージェント設計の 3 パターン（読取専用型・対話生成型・監査修正型）
- `agent_docs/naming-and-format.md` — ファイル命名・コードフェンス・構造の正規仕様
- `agent_docs/mcp-usage.md` — GitHub MCP / Context7 MCP の用途・利用パターン
- `agent_docs/tdd-template.md` — TDD セクションの独立リファレンス（t-wada 式サイクル）
- `agent_docs/prompt-engineering.md` — エージェント・スキル記述のプロンプトベストプラクティス集
