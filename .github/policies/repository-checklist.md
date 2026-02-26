# リポジトリ標準化チェックリスト

組織内のすべてのリポジトリが準拠すべき最低基準を定義します。
このチェックリストは `repo-guardian` エージェントおよび `repo-audit` スキルの根拠文書です。

## 必須項目

### セキュリティ（最優先）

- [ ] **SECURITY.md**: 脆弱性報告の連絡先と手順が明記されている
- [ ] **gitleaks**: CI でシークレット漏洩検知が有効化されている
- [ ] **Dependabot**: 最低限 `github-actions` エコシステムの自動更新が有効
- [ ] **LICENSE**: OSS の場合、適切なライセンスファイルが存在する

### 品質ゲート

- [ ] **CI ワークフロー**: PR に対して自動チェックが実行される
- [ ] **actionlint**: GitHub Actions 定義の静的解析
- [ ] **markdownlint**: ドキュメントの品質維持
- [ ] **yamllint**: 設定ファイルの構文保証

### 開発プロセス

- [ ] **PULL_REQUEST_TEMPLATE.md**: PR の品質を標準化するテンプレート
- [ ] **ISSUE_TEMPLATE**: バグ報告と機能要望のフォーム
- [ ] **CODEOWNERS**: レビュー責任の明確化
- [ ] **CONTRIBUTING.md**: 新規参加者向けの開発ガイド

### ドキュメント

- [ ] **README.md**: プロジェクトの目的・セットアップ手順・使い方

### 開発環境

- [ ] **devcontainer.json**: 統一された開発環境の定義（gh CLI・Docker 利用可能）
- [ ] **extensions.json**: VS Code 推奨拡張機能の定義

### AI コーディング

- [ ] **Copilot Hooks**: コード生成後の自動品質チェック（postSave / postCommand）
- [ ] **カスタムエージェント**: 用途別サブエージェントの定義（`.github/agents/`）
- [ ] **Agent Skills**: エージェントが参照するスキル定義（`.github/skills/`）

## 推奨項目

- [ ] **typos**: 誤字検知の CI 統合
- [ ] **CODE_OF_CONDUCT.md**: コミュニティ行動規範
- [ ] **copilot-instructions.md**: Copilot のリポジトリ固有指示
- [ ] **ブランチ保護ルール**: main ブランチへの直接 push 禁止・レビュー必須

## 適用の流れ

```
1. /repo-audit で監査 → レポート生成
2. /repo-apply-baseline で不足分を追加
3. PR レビュー → マージ
4. ブランチ保護・Rulesets は GitHub 設定画面で手動適用
```

## 更新履歴

| 日付 | 変更内容 |
|------|---------|
| 2026-02-14 | 初版作成 |
| 2026-02-14 | 開発環境（devcontainer・推奨拡張）、AI コーディング（Hooks・サブエージェント・git-workflow Skill）を追加 |
