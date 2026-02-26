# Copilot カスタム指示 — sample-app

## プロジェクト概要

sample-app は pioyan が開発するサンプルプロジェクトです。

## リポジトリ構成

```
.devcontainer/
└── devcontainer.json    # Dev Container 設定（gh CLI・推奨拡張）
.github/
├── agents/              # Custom Agents（Agent Builder・Repo Guardian・Code Reviewer・Docs Writer）
├── skills/              # Agent Skills（監査・適用・CI・Dependabot・Git ワークフロー）
├── policies/            # 組織ポリシー文書（チェックリスト・ツール一覧）
├── workflows/           # GitHub Actions CI
├── ISSUE_TEMPLATE/      # Issue テンプレート
├── CODEOWNERS           # コードオーナー
├── dependabot.yml       # 依存自動更新
└── PULL_REQUEST_TEMPLATE.md
.vscode/
├── settings.json        # エージェント・Hooks 設定
├── extensions.json      # 推奨拡張機能
└── mcp.json             # ローカル MCP サーバー設定
agent_docs/              # AI エージェント向けリファレンス（自己参照用）
human_docs/              # 人間向けドキュメント
```

## コーディング規約

- コミットメッセージは Conventional Commits に従う
- ブランチ名は `<type>/<short-description>` 形式
- PR は必ずテンプレートに従い、CI を通過させてからレビューを依頼する

## ビルド・テスト

<!-- TODO: 技術スタック確定後に具体的なコマンドを追記 -->

## CI

PR を作成すると以下の衛生チェックが自動実行されます:

- **actionlint**: GitHub Actions の静的解析
- **markdownlint**: Markdown の品質チェック
- **yamllint**: YAML の構文チェック
- **gitleaks**: シークレット漏洩検知
- **typos**: 誤字検知

## 開発環境

### Dev Container

`.devcontainer/devcontainer.json` で統一された開発環境を提供します:

- **ベースイメージ**: Microsoft Universal Image（言語非依存）
- **GitHub CLI**: `gh` コマンドが利用可能（初回は `gh auth login` で認証）
- **Docker**: MCP サーバー等の実行に必要な Docker が利用可能
- **推奨拡張**: コンテナ起動時に自動インストール

### Copilot Hooks

`.vscode/settings.json` で以下のフックが設定されています:

- **postSave**: `.md` ファイル保存時に markdownlint、`.yml`/`.yaml` ファイル保存時に yamllint を自動実行
- **postCommand**: コード変更後に typos チェックを自動実行

コード生成・編集のたびに品質チェックが自動で走るため、手動での lint 実行は不要です。

### サブエージェント連携

`chat.customAgentInSubagent.enabled: true` が有効化されており、
メインエージェントから以下のカスタムエージェントをサブエージェントとして呼び出すことができます。

## カスタムエージェント

このリポジトリには以下のカスタムエージェントが定義されています:

| エージェント | 用途 |
|------------|------|
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
