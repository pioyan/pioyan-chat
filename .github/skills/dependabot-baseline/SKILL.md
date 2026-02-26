---
name: dependabot-baseline
description: "Dependabotの最小構成を導入するスキル。まずGitHub Actionsの依存更新から始め、リポジトリの技術スタックに応じてエコシステムを追加する手順を提供します。依存管理の自動化を始めたいときに使用してください。"
---

# Dependabot ベースライン導入スキル

## 概要

Dependabot を「壊れにくい最小構成」から導入し、段階的にカバー範囲を広げる手順を提供します。

## 最小構成（必ず導入）

すべてのリポジトリに最低限適用すべき設定:

```yaml
# .github/dependabot.yml
version: 2
updates:
  # GitHub Actions の依存を週次で更新
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
      timezone: "Asia/Tokyo"
    commit-message:
      prefix: "ci"
    labels:
      - "dependencies"
      - "github-actions"
```

### なぜ GitHub Actions から始めるのか

- Actions のバージョン固定はセキュリティ上重要（サプライチェーン攻撃の防止）
- メジャーバージョンタグ（`@v4`）だけでなく、SHA 固定も推奨
- 壊れるリスクが最も低い（アプリケーションコードに影響しない）

## 技術スタック別の追加設定

リポジトリの技術スタックが判明したら、以下を段階的に追加してください:

### Node.js (npm / yarn / pnpm)

```yaml
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "deps"
    labels:
      - "dependencies"
    # セキュリティ更新のみを優先する場合
    # open-pull-requests-limit: 5
```

### Python (pip / poetry / pipenv)

```yaml
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "deps"
    labels:
      - "dependencies"
```

### Go (go modules)

```yaml
  - package-ecosystem: "gomod"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "deps"
    labels:
      - "dependencies"
```

### Docker

```yaml
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    commit-message:
      prefix: "deps"
    labels:
      - "dependencies"
```

## 運用のベストプラクティス

1. **PR 上限**: `open-pull-requests-limit` でオープンPR数を制限（デフォルト5）
2. **自動マージ**: セキュリティパッチは自動マージを検討（GitHub Actions で実現可能）
3. **グループ化**: 関連パッケージをグループ化して PR 数を削減

```yaml
    groups:
      dev-dependencies:
        dependency-type: "development"
      production-dependencies:
        dependency-type: "production"
```

4. **レビュアー指定**: `reviewers` で自動的にレビュアーを割り当て
