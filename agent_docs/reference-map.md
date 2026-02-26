# エージェント参照マップ

エージェントが**自分の立ち位置と利用可能なリソース**を即座に把握するための索引です。

## エージェント一覧とタイプ分類

| エージェント | タイプ | ツール | 主な役割 |
|------------|--------|--------|---------|
| `@agent-builder` | 対話生成型 | search, editFiles, runInTerminal, fetch | カスタムエージェント＋スキルの対話的設計・生成 |
| `@dev-env-builder` | 対話生成型 | search, editFiles, runInTerminal, fetch | 開発環境（Dev Container・CI・Dependabot）の構築 |
| `@repo-guardian` | 監査修正型 | search, editFiles, runInTerminal, fetch | リポジトリ監査 → 不足ファイル追加 → PR 作成 |
| `@code-reviewer` | 読取専用型 | search, fetch | PR 差分のレビューコメント提案 |
| `@docs-writer` | 読取専用型 | search, editFiles | コード変更に伴うドキュメント更新提案 |
| `@git-operator` | 対話生成型 | search, runInTerminal | Git 運用（ブランチ・コミット・PR・Issue・hotfix/release） |

### タイプの定義

- **読取専用型**: コードの分析・レビューを行い、提案のみ出力する。自動的なコード変更は行わない
- **対話生成型**: ユーザーにヒアリング → 設計提案 → 承認 → ファイル生成のフローを持つ
- **監査修正型**: 自動で監査を実行 → 問題を検出 → 修正を適用 → PR を作成する

> 各タイプの詳細な設計指針は [design-patterns.md](design-patterns.md) を参照。

## エージェント → スキル → ポリシー 参照チェーン

```text
@agent-builder
├── 参照: .github/agents/*.md（既存エージェントのフォーマット）
├── 参照: agent_docs/design-patterns.md
├── 参照: agent_docs/naming-and-format.md
├── 参照: agent_docs/tdd-template.md
├── 参照: agent_docs/prompt-engineering.md
├── 更新: .github/copilot-instructions.md
├── 更新: human_docs/agent-guide.md
└── 更新: human_docs/architecture.md

@dev-env-builder
├── スキル: .github/skills/dev-env-setup/SKILL.md
├── スキル: .github/skills/ci-hygiene/SKILL.md
├── スキル: .github/skills/dependabot-baseline/SKILL.md
├── 参照: agent_docs/mcp-usage.md
└── ポリシー: .github/policies/ci-tools.md

@repo-guardian
├── スキル: .github/skills/repo-audit/SKILL.md
│   └── ポリシー: .github/policies/repository-checklist.md
├── スキル: .github/skills/repo-apply-baseline/SKILL.md
└── 参照: agent_docs/reference-map.md（本ドキュメント）

@code-reviewer
├── スキル: .github/skills/git-workflow/SKILL.md
├── 参照: CONTRIBUTING.md
└── 参照: agent_docs/reference-map.md（本ドキュメント）

@git-operator
├── スキル: .github/skills/git-workflow/SKILL.md
├── 参照: CONTRIBUTING.md
├── 参照: .github/PULL_REQUEST_TEMPLATE.md
└── 参照: .github/ISSUE_TEMPLATE/ (bug_report.yml, feature_request.yml)

@docs-writer
├── 参照: agent_docs/reference-map.md（本ドキュメント）
├── 参照: agent_docs/naming-and-format.md
├── 対象: README.md / CONTRIBUTING.md / SECURITY.md
├── 対象: .github/copilot-instructions.md
├── 対象: .github/skills/*/SKILL.md
└── 対象: .github/policies/*.md
```

## スキル一覧

| スキル | パス | 概要 | 参照元エージェント |
|--------|------|------|-----------------|
| `/repo-audit` | `.github/skills/repo-audit/SKILL.md` | リポジトリ監査チェックリストと手順 | `@repo-guardian` |
| `/repo-apply-baseline` | `.github/skills/repo-apply-baseline/SKILL.md` | 不足ファイルの優先度別追加ルール | `@repo-guardian` |
| `/ci-hygiene` | `.github/skills/ci-hygiene/SKILL.md` | CI 衛生チェック（5 ツール）の構成テンプレート | `@dev-env-builder` |
| `/dependabot-baseline` | `.github/skills/dependabot-baseline/SKILL.md` | Dependabot の段階的導入テンプレート | `@dev-env-builder` |
| `/dev-env-setup` | `.github/skills/dev-env-setup/SKILL.md` | 5 言語対応の開発環境テンプレート集 | `@dev-env-builder` |
| `/git-workflow` | `.github/skills/git-workflow/SKILL.md` | ブランチ・コミット・PR・rebase の標準手順 | `@code-reviewer`, `@git-operator` |

## ポリシー文書

| ファイル | パス | 概要 | 参照元 |
|---------|------|------|--------|
| CI ツール仕様 | `.github/policies/ci-tools.md` | actionlint・markdownlint 等の詳細仕様 | `/ci-hygiene` スキル |
| リポジトリチェックリスト | `.github/policies/repository-checklist.md` | 必須・推奨ファイルのチェックリスト | `/repo-audit` スキル |

## 設定ファイル

| ファイル | パス | 概要 |
|---------|------|------|
| VS Code 設定 | `.vscode/settings.json` | Copilot Hooks・エージェント設定 |
| 推奨拡張 | `.vscode/extensions.json` | VS Code 推奨拡張機能リスト |
| MCP サーバー | `.vscode/mcp.json` | GitHub MCP / Context7 MCP の接続定義 |
| Dev Container | `.devcontainer/devcontainer.json` | 開発コンテナの構成 |
| Copilot 指示 | `.github/copilot-instructions.md` | 全エージェント共通のプロジェクトコンテキスト |

## 4 層アーキテクチャ

```text
┌─────────────────────────────────────────────────┐
│  Layer 1: カスタムエージェント (.github/agents/) │
│  ── 判断と実行を担うトップレベルの AI エージェント │
├─────────────────────────────────────────────────┤
│  Layer 2: スキル (.github/skills/)              │
│  ── 手順・テンプレートの知識ベース                │
├─────────────────────────────────────────────────┤
│  Layer 3: ポリシー・設定                         │
│  ── .github/policies/ / .vscode/ / agent_docs/  │
│  ── 判断基準・仕様・リファレンス                  │
├─────────────────────────────────────────────────┤
│  Layer 4: コミュニティヘルスファイル              │
│  ── README / CONTRIBUTING / SECURITY / LICENSE   │
└─────────────────────────────────────────────────┘
```

エージェントは Layer 1 → Layer 2 → Layer 3 の順に参照し、
Layer 4 のファイルを生成・更新対象として扱います。
