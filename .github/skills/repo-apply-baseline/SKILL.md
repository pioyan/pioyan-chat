---
name: repo-apply-baseline
description: "監査結果に基づき、不足しているベストプラクティスファイルをリポジトリに追加するスキル。テンプレート、CI、Dependabot、セキュリティ文書などを最小差分で適用します。リポジトリの標準化を実施したいときに使用してください。"
---

# ベースライン適用スキル

## 概要

`/repo-audit` スキルの結果をもとに、不足しているファイルをリポジトリに追加します。
既存ファイルがある場合は上書きせず、差分のみを提案します。

## 適用ルール

### 基本原則

1. **既存ファイルを尊重**: すでに存在するファイルは変更しない（明らかな不備がある場合のみ提案）
2. **リポジトリのスタイルに合わせる**: 既存の Markdown スタイル・言語・フォーマットを踏襲する
3. **プレースホルダーを明示**: リポジトリ固有の情報が必要な箇所は `<!-- TODO: ... -->` で明示する
4. **1 PR にまとめる**: 関連する変更は1つのPRにまとめる

### 優先度順の適用

監査で見つかった不足項目を、以下の優先度で適用してください:

#### 優先度: 高（セキュリティ・品質ゲート）

1. `SECURITY.md` — 脆弱性報告導線の整備
2. `.github/workflows/ci.yml` — 基本 CI の導入
3. `.github/dependabot.yml` — 依存更新の自動化
4. `LICENSE` — ライセンスファイル

#### 優先度: 中（開発プロセス標準化）

1. `.github/PULL_REQUEST_TEMPLATE.md` — PR テンプレート
2. `.github/ISSUE_TEMPLATE/bug_report.yml` — バグ報告フォーム
3. `.github/ISSUE_TEMPLATE/feature_request.yml` — 機能要望フォーム
4. `.github/CODEOWNERS` — コードオーナー
5. `CONTRIBUTING.md` — 開発参加ガイド

#### 優先度: 低（推奨）

1. `README.md` — プロジェクト説明の充実
2. `.github/copilot-instructions.md` — Copilot カスタム指示
3. `CODE_OF_CONDUCT.md` — 行動規範
4. `agent_docs/` — AI エージェント向けリファレンス（カスタムエージェント存在時）

## 適用後の検証

ファイル追加後、以下の検証を行ってください:

1. **YAML 構文チェック**: `yamllint` で `.yml` / `.yaml` ファイルを検証
2. **Markdown 構文チェック**: `markdownlint` で `.md` ファイルを検証
3. **Actions 検証**: `actionlint` で workflow ファイルを検証
4. **テンプレート表示確認**: Issue/PR テンプレートが正しく認識されるか確認

## PR テンプレート

適用 PR は以下の形式で作成してください:

```markdown
## 🛡️ リポジトリベストプラクティスの適用

### 変更概要
組織標準のベストプラクティスに基づき、以下のファイルを追加しました。

### 追加ファイル
- [ ] {ファイルパス}: {追加理由}

### チェックリスト
- [ ] 既存ファイルへの影響なし
- [ ] YAML 構文チェック通過
- [ ] Markdown 構文チェック通過
- [ ] テンプレートの UI 表示確認

### 参照ポリシー
- [リポジトリチェックリスト](.github/policies/repository-checklist.md)
```
