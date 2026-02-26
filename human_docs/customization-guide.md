# カスタマイズガイド

develop-base テンプレートを新しいプロジェクトで使う際に、
変更が必要なファイルと箇所を網羅的にまとめたガイドです。

## 変更の優先度

変更箇所を 3 段階の優先度に分類しています:

- **必須** — そのまま使うとリンク切れやオーナー不一致が起きるため、最初に変更してください
- **技術スタック依存** — 使用する言語・フレームワーク確定後に変更（`@dev-env-builder` で自動化可能）
- **推奨** — プロジェクト固有の情報追記。TODO コメントが目印

---

## 1. 必須: プロジェクト固有文字列の置換

以下の文字列がハードコードされています。全ファイル横断で置換してください。

### `sample-app` → プロジェクト名

| ファイル | 箇所 |
|---------|------|
| `README.md` | タイトル `# sample-app`・概要・clone URL（2 箇所） |
| `CONTRIBUTING.md` | タイトル・Issue テンプレート URL（3 箇所） |
| `SECURITY.md` | Security Advisory URL |
| `.github/copilot-instructions.md` | タイトル・プロジェクト概要 |
| `.github/ISSUE_TEMPLATE/config.yml` | Discussions URL |

### `pioyan` → オーナー名（GitHub ユーザー名 / 組織名）

| ファイル | 箇所 |
|---------|------|
| `LICENSE` | `Copyright (c) 2026 pioyan` |
| `.github/CODEOWNERS` | 全行のオーナー指定（4 箇所） |
| `.github/copilot-instructions.md` | プロジェクト概要 |
| `README.md` | clone URL（2 箇所） |
| `CONTRIBUTING.md` | Issue / Feature / Discussions URL（3 箇所） |
| `SECURITY.md` | Security Advisory URL |
| `.github/ISSUE_TEMPLATE/config.yml` | Discussions URL |

### `security@example.com` → セキュリティ報告先メール

| ファイル | 箇所 |
|---------|------|
| `SECURITY.md` | メール連絡先 |

### `develop-base` → プロジェクト名

| ファイル | 箇所 |
|---------|------|
| `.devcontainer/devcontainer.json` | `"name"` フィールド |

### `2026` → 著作権年（必要に応じて）

| ファイル | 箇所 |
|---------|------|
| `LICENSE` | `Copyright (c)` の年 |

---

## 2. 技術スタック依存: 開発環境の構成

使用する言語・フレームワークが決まったら変更するファイルです。
`@dev-env-builder` エージェントで対話的に自動生成できます。

### `.devcontainer/devcontainer.json`

| 項目 | 現在の値 | 変更内容 |
|------|---------|---------|
| `image` | `mcr.microsoft.com/devcontainers/universal:5.1.4` | 言語固有イメージに変更 |
| `features` | GitHub CLI + Docker | 言語固有の Feature を追加 |
| `postCreateCommand` | `echo` のみ | 依存インストールコマンドに変更 |
| `extensions` | 汎用 7 拡張 | 言語固有拡張を追加 |
| `settings` | ターミナルのみ | 言語固有設定を追加 |

#### 言語別のベースイメージ例

| 言語 | イメージ |
|------|---------|
| Node.js | `mcr.microsoft.com/devcontainers/javascript-node:22` |
| Python | `mcr.microsoft.com/devcontainers/python:3.13` |
| Go | `mcr.microsoft.com/devcontainers/go:1.23` |
| Rust | `mcr.microsoft.com/devcontainers/rust:latest` |
| Java | `mcr.microsoft.com/devcontainers/java:21` |

DB やキャッシュが必要な場合は `docker-compose.yml` を追加し、
`devcontainer.json` で `dockerComposeFile` を参照する構成に変更します。

### `.github/workflows/ci.yml`

既存の 5 つの衛生チェックジョブ（actionlint / markdownlint / yamllint / gitleaks / typos）は
**そのまま保持** し、言語固有のビルド・テストジョブを **追加** してください。

```yaml
# 追加ジョブの例（Node.js）
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

### `.github/dependabot.yml`

現在は `github-actions` エコシステムのみ有効です。
言語に合わせてエコシステムを追加してください。

| 言語 | `package-ecosystem` |
|------|-------------------|
| Node.js | `npm` |
| Python | `pip` |
| Go | `gomod` |
| Rust | `cargo` |
| Java (Maven) | `maven` |
| Java (Gradle) | `gradle` |
| Docker | `docker` |

### `.vscode/settings.json`

言語固有のリンター・フォーマッター用 Copilot Hooks を追加できます:

```jsonc
// postSave フック追加例
{
  "command": "npx eslint --fix ${file}",
  "filePattern": "**/*.{ts,tsx,js,jsx}"
}
```

### `.vscode/extensions.json`

既存の 7 拡張は共通で保持し、言語固有の拡張を `recommendations` に追加:

| 言語 | 追加する拡張 ID |
|------|---------------|
| Node.js | `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode` |
| Python | `ms-python.python`, `charliermarsh.ruff` |
| Go | `golang.go` |
| Rust | `rust-lang.rust-analyzer` |
| Java | `vscjava.vscode-java-pack` |

---

## 3. 推奨: TODO コメントの記入

テンプレート内の `<!-- TODO: ... -->` コメントを検索し、
プロジェクト固有の情報を記入してください。

```bash
grep -rn "TODO" --include="*.md" .
```

### `README.md`

| TODO | 記入内容 |
|------|---------|
| プロジェクトの説明 | プロジェクトの目的・概要 |
| 追加の前提条件 | 言語ランタイム等（Dev Container 利用時は不要な場合もある） |
| インストールコマンド | `npm ci` / `pip install` 等 |
| 起動コマンド | `npm run dev` / `python manage.py runserver` 等 |
| 基本的な使い方 | アプリケーションの利用手順 |

### `SECURITY.md`

| TODO | 記入内容 |
|------|---------|
| セキュリティ連絡先メール | 実際のセキュリティ報告先 |
| サポートバージョンの表 | サポート対象バージョンの一覧 |

### `CONTRIBUTING.md`

| TODO | 記入内容 |
|------|---------|
| コーディング規約 | プロジェクト固有のスタイルガイド・規約 |

### `.github/copilot-instructions.md`

| TODO | 記入内容 |
|------|---------|
| ビルド・テストコマンド | `npm ci && npm test` 等の具体的コマンド |

---

## 4. 変更不要なファイル

以下のファイルはプロジェクトに関わらずそのまま使用できます:

| ファイル | 理由 |
|---------|------|
| `.github/workflows/ci.yml`（既存ジョブ） | 言語非依存の衛生チェック |
| `.github/PULL_REQUEST_TEMPLATE.md` | 汎用 PR テンプレート |
| `.github/ISSUE_TEMPLATE/bug_report.yml` | 汎用バグ報告フォーム |
| `.github/ISSUE_TEMPLATE/feature_request.yml` | 汎用機能要望フォーム |
| `.vscode/mcp.json` | GitHub MCP Server 設定 |
| `.github/agents/` 配下の全エージェント | 汎用エージェント定義 |
| `.github/skills/` 配下の全スキル | 汎用スキル定義 |
| `.github/policies/` 配下のポリシー文書 | 組織標準のリファレンス |
| `CODE_OF_CONDUCT.md` | 汎用行動規範 |

---

## カスタマイズの自動化

手動での変更が面倒な場合は、以下のエージェントを活用できます:

| やりたいこと | 使うエージェント |
|------------|----------------|
| 言語に合わせた開発環境の一括構築 | `@dev-env-builder` |
| 変更後のドキュメント更新 | `@docs-writer` |
| 設定漏れのチェック | `@repo-guardian` |

詳細は [agent-guide.md](agent-guide.md) を参照してください。
