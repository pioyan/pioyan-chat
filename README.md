# sample-app

<!-- TODO: プロジェクトの説明を記入してください -->

## 概要

sample-app は...（プロジェクトの目的・概要をここに記述）

## セットアップ

### 前提条件

- [VS Code](https://code.visualstudio.com/) + [Dev Containers 拡張](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker](https://www.docker.com/)（Dev Container・MCP サーバー実行用）

<!-- TODO: 技術スタック確定後に追加の前提条件を記入してください -->

### Dev Container で開始（推奨）

```bash
git clone https://github.com/pioyan/sample-app.git
cd sample-app
```

1. VS Code でフォルダを開く
2. コマンドパレット → **Dev Containers: Reopen in Container** を実行
3. コンテナが起動したら、ターミナルで GitHub CLI を認証:

```bash
gh auth login
```

> **Note**: 推奨拡張機能はコンテナ起動時に自動インストールされます。

### ローカル開発（Dev Container を使わない場合）

```bash
git clone https://github.com/pioyan/sample-app.git
cd sample-app
# TODO: インストールコマンドを記入してください
```

VS Code の推奨拡張が `.vscode/extensions.json` に定義されています。
初回起動時に表示されるプロンプトからインストールしてください。

### 開発サーバーの起動

```bash
# TODO: 起動コマンドを記入してください
```

## AI コーディング環境

このリポジトリは GitHub Copilot を活用した AI コーディングに最適化されています。

### Copilot Hooks

コード生成・編集後に品質チェックが自動実行されます（`.vscode/settings.json` で設定）:

| フック | 対象 | 実行コマンド |
|--------|------|------------|
| postSave | `*.md` | markdownlint |
| postSave | `*.yml` / `*.yaml` | yamllint |
| postCommand | 全ファイル | typos |

### カスタムエージェント

Copilot Chat から以下のエージェントを呼び出せます:

| エージェント | 用途 |
|------------|------|
| `@repo-guardian` | リポジトリ標準化の監査・適用 |
| `@code-reviewer` | PR レビューコメントの提案 |
| `@docs-writer` | ドキュメント更新提案の生成 |

### Agent Skills

| スキル | 内容 |
|--------|------|
| `/repo-audit` | ベストプラクティス準拠の監査 |
| `/repo-apply-baseline` | 不足ファイルの追加 |
| `/ci-hygiene` | CI 衛生チェックの導入 |
| `/dependabot-baseline` | Dependabot の最小構成導入 |
| `/git-workflow` | Git 運用の標準手順 |

## 使い方

<!-- TODO: 基本的な使い方を記入してください -->

## 開発に参加する

開発への参加方法は [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

## セキュリティ

脆弱性の報告方法は [SECURITY.md](SECURITY.md) をご覧ください。

## ライセンス

<!-- TODO: ライセンスを記入してください -->

このプロジェクトは [MIT License](LICENSE) の下で公開されています。
