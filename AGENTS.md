# AGENTS

develop-base で利用できる **カスタムエージェント** と **Agent Skills** の一覧・使い分け・おすすめフローをまとめます。

> 詳細ガイドは [human_docs/agent-guide.md](human_docs/agent-guide.md) を参照してください。

## 前提

- VS Code + GitHub Copilot Chat
- （推奨）Dev Container

## 使い方（基本）

### カスタムエージェント

Copilot Chat で `@エージェント名` を先頭に付けて呼び出します。

例:

```text
@repo-guardian このリポジトリのベストプラクティス準拠状況を確認してください
```

### Agent Skills

Skills は手順書です。Copilot Chat で `/スキル名` として直接呼び出すこともできます。

例:

```text
/repo-audit を実行して、未準拠項目を一覧化してください
```

## カスタムエージェント一覧

- `@dev-env-builder` — 開発環境（Dev Container / CI / Dependabot / VS Code設定など）を対話的に構築
  - 定義: [.github/agents/dev-env-builder.md](.github/agents/dev-env-builder.md)
- `@repo-guardian` — リポジトリのベストプラクティス準拠を監査し、不足分を最小差分で追加してPR化
  - 定義: [.github/agents/repo-guardian.md](.github/agents/repo-guardian.md)
- `@code-reviewer` — PR差分を読み、品質・セキュリティ・テスト観点でレビューコメント案を提案
  - 定義: [.github/agents/code-reviewer.md](.github/agents/code-reviewer.md)
- `@docs-writer` — 変更に伴う README/CONTRIBUTING/Skills/Policies 等のドキュメント更新を提案・反映
  - 定義: [.github/agents/docs-writer.md](.github/agents/docs-writer.md)
- `@agent-builder` — プロジェクト固有のカスタムエージェント/スキルを対話的に設計・生成（コード実装エージェントにはTDDを組み込み）
  - 定義: [.github/agents/agent-builder.md](.github/agents/agent-builder.md)
- `@git-operator` — Git運用に精通した専門エージェント。ブランチ・コミット・rebase・PR・Issue・hotfix/releaseを規約に沿って実行
  - 定義: [.github/agents/git-operator.md](.github/agents/git-operator.md)

## Agent Skills 一覧

- `/dev-env-setup` — 言語別テンプレートとヒアリングガイドに基づく開発環境セットアップ手順
  - 定義: [.github/skills/dev-env-setup/SKILL.md](.github/skills/dev-env-setup/SKILL.md)
- `/repo-audit` — リポジトリのベストプラクティス準拠状況を監査
  - 定義: [.github/skills/repo-audit/SKILL.md](.github/skills/repo-audit/SKILL.md)
- `/repo-apply-baseline` — 監査結果に基づき、不足ファイルを最小差分で追加
  - 定義: [.github/skills/repo-apply-baseline/SKILL.md](.github/skills/repo-apply-baseline/SKILL.md)
- `/ci-hygiene` — actionlint/markdownlint/yamllint/gitleaks/typos など言語非依存の衛生CIを導入
  - 定義: [.github/skills/ci-hygiene/SKILL.md](.github/skills/ci-hygiene/SKILL.md)
- `/dependabot-baseline` — Dependabotを最小構成から段階的に導入
  - 定義: [.github/skills/dependabot-baseline/SKILL.md](.github/skills/dependabot-baseline/SKILL.md)
- `/git-workflow` — ブランチ命名・Conventional Commits・PR作法・rebase・hotfix/release を標準化
  - 定義: [.github/skills/git-workflow/SKILL.md](.github/skills/git-workflow/SKILL.md)

## おすすめの利用フロー

### 新規プロジェクト立ち上げ時

```text
1. @dev-env-builder で開発環境を構築
2. @agent-builder でプロジェクト固有のエージェントを作成（必要な場合）
3. @repo-guardian で設定漏れを監査・不足分をPR化
4. @docs-writer でドキュメントの整合性を更新
```

### 日常の開発サイクル

```text
1. feature ブランチで実装（必要なら /git-workflow を参照）
2. @code-reviewer でセルフレビュー
3. @docs-writer でドキュメント更新を確認
4. PR 作成 → CI 通過を確認
```

### リポジトリの健全性チェック（定期）

```text
1. @repo-guardian で監査を実施
2. 不足分のPRを作成
3. Dependabot 更新状況を確認（必要に応じて /dependabot-baseline を参照）
```

## 関連リンク

- 使い方の詳細: [human_docs/agent-guide.md](human_docs/agent-guide.md)
- Copilot カスタム指示: [.github/copilot-instructions.md](.github/copilot-instructions.md)
- 参加・規約: [CONTRIBUTING.md](CONTRIBUTING.md)
