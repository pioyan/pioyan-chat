# Contributing Guide

sample-app への貢献にご興味をいただきありがとうございます！
このドキュメントでは、プロジェクトへの参加方法を説明します。

## 開発の流れ

### 1. Issue の作成

- バグを見つけた場合は
  [Bug Report](https://github.com/pioyan/sample-app/issues/new?template=bug_report.yml)
  テンプレートを使用してください
- 新機能の提案は
  [Feature Request](https://github.com/pioyan/sample-app/issues/new?template=feature_request.yml)
  テンプレートを使用してください
- 作業を開始する前に、既存の Issue を確認し、重複がないか確認してください

### 2. ブランチの作成

```bash
# メインブランチを最新に
git checkout main
git pull origin main

# 作業ブランチを作成
git checkout -b <type>/<short-description>
```

**ブランチ命名規則**:

- `feat/` — 新機能
- `fix/` — バグ修正
- `docs/` — ドキュメントのみの変更
- `refactor/` — リファクタリング
- `ci/` — CI/CD の変更
- `chore/` — その他の雑務

### 3. コミット

コミットメッセージは
[Conventional Commits](https://www.conventionalcommits.org/)
に従ってください:

```text
<type>(<scope>): <subject>

<body>

<footer>
```

**type の一覧**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `ci`, `chore`

### 4. Pull Request の作成

1. 変更を push し、PR を作成します
2. PR テンプレートに従って変更内容を記述します
3. CI のチェックがすべて通過することを確認します
4. レビュアーのフィードバックに対応します

## コーディング規約

<!-- TODO: プロジェクト固有のコーディング規約を追記してください -->

- 一貫性のあるコードスタイルを維持してください
- 意味のある変数名・関数名を使用してください
- 必要に応じてコメントを追加してください
- テストを書いてください

## 質問・サポート

- 開発に関する質問は [Discussions](https://github.com/pioyan/sample-app/discussions) をご利用ください
- バグ報告とは別に、使い方の質問もこちらで受け付けています
