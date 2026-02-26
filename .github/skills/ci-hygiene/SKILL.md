---
name: ci-hygiene
description: "言語非依存のCI衛生チェックを導入するスキル。actionlint、markdownlint、yamllint、gitleaks、typosをGitHub Actionsワークフローとして構成します。CIの初期導入や改善時に使用してください。"
---

# CI 衛生チェック導入スキル

## 概要

リポジトリに言語・フレームワーク非依存の「衛生チェック CI」を導入します。
アプリケーション固有のビルド・テストとは独立して動作し、設定ファイルやドキュメントの品質を担保します。

## 推奨ツールセット

| ツール | 目的 | 重要度 |
|--------|------|--------|
| [actionlint](https://github.com/rhysd/actionlint) | GitHub Actions ワークフローの静的解析 | 必須 |
| [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) | Markdown の品質・一貫性チェック | 必須 |
| [yamllint](https://github.com/adrienverge/yamllint) | YAML の構文・スタイルチェック | 必須 |
| [gitleaks](https://github.com/gitleaks/gitleaks) | コミット内のシークレット漏洩検知 | 必須 |
| [typos](https://github.com/crate-ci/typos) | ソースコード・ドキュメントの誤字検知 | 推奨 |

## ワークフロー構成ガイド

### 基本構造

```yaml
name: CI — Repo Hygiene
on:
  pull_request:
  push:
    branches: [main]

jobs:
  actionlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: reviewdog/action-actionlint@v1

  markdownlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: DavidAnson/markdownlint-cli2-action@v19

  yamllint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ibiqlik/action-yamllint@v3

  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  typos:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: crate-ci/typos@master
```

### カスタマイズのポイント

1. **markdownlint**: `.markdownlint.yml` でルールをカスタマイズ可能
2. **yamllint**: `.yamllint.yml` でルールをカスタマイズ可能
3. **gitleaks**: `.gitleaks.toml` で許可リストを設定可能（誤検知対策）
4. **typos**: `_typos.toml` で辞書・除外パターンを設定可能

### 段階導入の推奨

初回導入時はすべてのジョブを `continue-on-error: true` にし、
既存の問題を把握してから段階的に必須化することを推奨します:

```yaml
  markdownlint:
    runs-on: ubuntu-latest
    continue-on-error: true  # 初回導入時。安定したら削除
```

## リポジトリ固有のテスト追加

衛生チェック CI が安定した後、リポジトリの技術スタックに応じたテストジョブを追加してください:

- **Node.js**: `npm ci && npm test`
- **Python**: `pip install -e ".[dev]" && pytest`
- **Go**: `go test ./...`
- **Rust**: `cargo test`

これらは衛生チェックとは別のジョブとして追加し、衛生チェックを壊さないようにします。
