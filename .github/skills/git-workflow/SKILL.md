````skill
---
name: git-workflow
description: "Git の運用手順を標準化するスキル。ブランチ戦略、Conventional Commits、PR 作法、rebase 運用、hotfix・release フローをカバーします。エージェントが Git 操作を指示された際の一次参照先として使用してください。"
---

# Git ワークフロースキル

## 概要

このスキルは、リポジトリにおける Git 運用の標準手順を定義します。
基本ルールは [CONTRIBUTING.md](../../../CONTRIBUTING.md) に準拠し、本スキルではエージェントが
具体的な `git` コマンドを生成できるレベルの詳細手順を提供します。

## ブランチ戦略

### ブランチ命名規則

| プレフィックス | 用途 | 例 |
|--------------|------|-----|
| `feat/` | 新機能 | `feat/add-login-page` |
| `fix/` | バグ修正 | `fix/null-pointer-error` |
| `docs/` | ドキュメントのみ | `docs/update-readme` |
| `refactor/` | リファクタリング | `refactor/extract-helper` |
| `ci/` | CI/CD の変更 | `ci/add-deploy-workflow` |
| `chore/` | その他の雑務 | `chore/update-deps` |
| `hotfix/` | 緊急修正 | `hotfix/critical-auth-bug` |
| `release/` | リリース準備 | `release/v1.2.0` |

### ブランチ作成手順

```bash
# 1. main を最新に同期
git checkout main
git pull origin main

# 2. 作業ブランチを作成
git checkout -b <type>/<short-description>
```

## Conventional Commits

### コミットメッセージ形式

```text
<type>(<scope>): <subject>

<body>

<footer>
```

### type 一覧

| type | 説明 | SemVer 影響 |
|------|------|------------|
| `feat` | 新機能 | MINOR |
| `fix` | バグ修正 | PATCH |
| `docs` | ドキュメントのみ | なし |
| `style` | フォーマット変更（動作影響なし） | なし |
| `refactor` | リファクタリング | なし |
| `test` | テストの追加・修正 | なし |
| `ci` | CI/CD の変更 | なし |
| `chore` | ビルド・補助ツールの変更 | なし |

### 破壊的変更（BREAKING CHANGE）

```text
feat(api)!: change authentication endpoint

BREAKING CHANGE: /auth/login は /api/v2/auth/login に変更されました。
旧エンドポイントは v2.0.0 で削除されます。
```

### コミット例

```bash
# 機能追加
git commit -m "feat(auth): add OAuth2 login support"

# バグ修正（Issue 参照付き）
git commit -m "fix(parser): handle empty input gracefully

Closes #42"

# ドキュメント更新
git commit -m "docs: update setup instructions in README"
```

## Pull Request 作法

### Step 1: PR 作成前の準備

```bash
# main の最新を取り込む（rebase 推奨）
git fetch origin
git rebase origin/main

# コンフリクトがある場合は解消してから続行
# git add <resolved-files>
# git rebase --continue

# リモートに push（rebase 後は force-push が必要）
git push --force-with-lease origin <branch-name>
```

### Step 2: PR の作成

```bash
# gh CLI で PR を作成
gh pr create \
  --title "<type>(<scope>): <subject>" \
  --body-file .github/PULL_REQUEST_TEMPLATE.md \
  --base main
```

### Step 3: PR チェックリスト

| 項目 | 確認内容 |
|------|---------|
| タイトル | Conventional Commits 形式になっている |
| 説明 | PR テンプレートに従って記入されている |
| CI | すべてのチェックが通過している |
| レビュー | 適切なレビュアーがアサインされている |
| ブランチ | `main` への直接コミットではない |

## Rebase 運用

### 基本方針

- **feature ブランチ → main**: rebase を推奨（履歴を直線的に保つ）
- **main → feature ブランチへの同期**: `git rebase origin/main` を使用
- **共有ブランチ**: rebase 禁止（他の開発者の履歴を壊さない）

### Interactive Rebase（コミット整理）

```bash
# 直近 N コミットを整理
git rebase -i HEAD~N

# エディタで以下の操作を選択:
# pick   — そのまま残す
# squash — 直前のコミットに統合（メッセージ編集）
# fixup  — 直前のコミットに統合（メッセージ破棄）
# reword — コミットメッセージを変更
# drop   — コミットを削除
```

### Rebase 時の注意事項

| 状況 | 対応 |
|------|------|
| rebase 後の push | `git push --force-with-lease`（`--force` は使わない） |
| コンフリクト発生 | 1 コミットずつ解消 → `git rebase --continue` |
| rebase 中断 | `git rebase --abort` で元の状態に戻る |
| 共有ブランチ | rebase **禁止** → merge を使用 |

## Hotfix フロー

緊急のバグ修正が必要な場合の手順です。

### Step 1: Hotfix ブランチ作成

```bash
git checkout main
git pull origin main
git checkout -b hotfix/<description>
```

### Step 2: 修正・コミット

```bash
# 最小限の修正を適用
git add <fixed-files>
git commit -m "fix(<scope>): <urgent fix description>"
```

### Step 3: PR 作成（緊急レビュー）

```bash
gh pr create \
  --title "fix(<scope>): <urgent fix description>" \
  --label "hotfix,priority:critical" \
  --base main
```

### Step 4: マージ後の対応

```bash
# 進行中の feature ブランチに hotfix を反映
git checkout feat/<feature-branch>
git rebase origin/main
```

## Release フロー

### Step 1: Release ブランチ作成

```bash
git checkout main
git pull origin main
git checkout -b release/v<major>.<minor>.<patch>
```

### Step 2: バージョン更新・CHANGELOG

```bash
# バージョンファイルやパッケージ設定を更新
# CHANGELOG.md にリリースノートを追記

git add -A
git commit -m "chore(release): prepare v<major>.<minor>.<patch>"
```

### Step 3: マージ・タグ付け

```bash
# PR でマージ後にタグを作成
git checkout main
git pull origin main
git tag -a v<major>.<minor>.<patch> -m "Release v<major>.<minor>.<patch>"
git push origin v<major>.<minor>.<patch>
```

### Step 4: GitHub Release 作成

```bash
gh release create v<major>.<minor>.<patch> \
  --title "v<major>.<minor>.<patch>" \
  --generate-notes
```

## クイックリファレンス

| やりたいこと | コマンド |
|------------|---------|
| ブランチ一覧 | `git branch -a` |
| ブランチ切替 | `git checkout <branch>` |
| 変更の一時退避 | `git stash` / `git stash pop` |
| 直前コミット修正 | `git commit --amend` |
| 特定コミットの取消 | `git revert <commit-hash>` |
| リモートの最新取得 | `git fetch origin` |
| ブランチ削除 | `git branch -d <branch>` |
| PR の状態確認 | `gh pr status` |
| PR のチェック結果 | `gh pr checks` |

````
