# アーキテクチャ概要

develop-base リポジトリの構成と各ファイルの役割を説明します。

## ディレクトリ構造

```text
develop-base/
├── .devcontainer/
│   └── devcontainer.json        # Dev Container 設定
├── .github/
│   ├── agents/                  # カスタムエージェント定義
│   │   ├── agent-builder.md     #   エージェント作成メタエージェント
│   │   ├── code-reviewer.md     #   PR レビューエージェント
│   │   ├── dev-env-builder.md   #   開発環境構築エージェント
│   │   ├── docs-writer.md       #   ドキュメント更新エージェント
│   │   ├── git-operator.md      #   Git 運用エージェント
│   │   └── repo-guardian.md     #   リポジトリ標準化エージェント
│   ├── skills/                  # エージェントスキル（手順書）
│   │   ├── ci-hygiene/          #   CI 衛生チェック導入
│   │   ├── dependabot-baseline/ #   Dependabot 最小構成
│   │   ├── dev-env-setup/       #   開発環境セットアップ
│   │   ├── git-workflow/        #   Git 運用標準手順
│   │   ├── repo-apply-baseline/ #   ベースライン適用
│   │   └── repo-audit/          #   リポジトリ監査
│   ├── policies/                # 組織ポリシー文書
│   │   ├── ci-tools.md          #   CI ツール仕様一覧
│   │   └── repository-checklist.md  # リポジトリチェックリスト
│   ├── workflows/
│   │   └── ci.yml               # GitHub Actions CI ワークフロー
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml       #   バグ報告フォーム
│   │   ├── config.yml           #   Issue テンプレート設定
│   │   └── feature_request.yml  #   機能要望フォーム
│   ├── CODEOWNERS               # コードオーナー定義
│   ├── copilot-instructions.md  # Copilot カスタム指示
│   ├── dependabot.yml           # Dependabot 設定
│   └── PULL_REQUEST_TEMPLATE.md # PR テンプレート
├── .vscode/
│   ├── extensions.json          # 推奨 VS Code 拡張
│   ├── mcp.json                 # MCP サーバー設定
│   └── settings.json            # エディタ・Hooks 設定
├── human_docs/                  # 人間向けドキュメント（本ディレクトリ）
├── agent_docs/                  # AI エージェント向けリファレンス
│   ├── README.md                #   ドキュメント一覧・インデックス
│   ├── reference-map.md         #   エージェント参照マップ
│   ├── design-patterns.md       #   エージェント設計パターン
│   ├── naming-and-format.md     #   命名・フォーマット仕様
│   ├── mcp-usage.md             #   MCP サーバー利用ガイド
│   ├── tdd-template.md          #   TDD セクションテンプレート
│   └── prompt-engineering.md    #   プロンプトエンジニアリングガイド
├── CODE_OF_CONDUCT.md           # 行動規範
├── CONTRIBUTING.md              # 開発参加ガイド
├── LICENSE                      # MIT ライセンス
├── README.md                    # プロジェクト README
└── SECURITY.md                  # セキュリティポリシー
```

---

## レイヤー構成

このリポジトリは 4 つのレイヤーで構成されています:

```text
┌─────────────────────────────────────────────┐
│           カスタムエージェント層              │
│  @agent-builder   @dev-env-builder        │
│  @repo-guardian    @code-reviewer           │
│  @docs-writer      @git-operator             │
├─────────────────────────────────────────────┤
│              スキル層                        │
│  /dev-env-setup  /repo-audit                 │
│  /ci-hygiene     /dependabot-baseline        │
│  /repo-apply-baseline  /git-workflow         │
├─────────────────────────────────────────────┤
│           ポリシー・設定層                    │
│  policies/   workflows/   dependabot.yml     │
│  .vscode/    .devcontainer/                  │
│  agent_docs/                                 │
├─────────────────────────────────────────────┤
│        コミュニティヘルスファイル層            │
│  README  CONTRIBUTING  SECURITY  LICENSE     │
│  CODE_OF_CONDUCT  CODEOWNERS                 │
│  ISSUE_TEMPLATE/  PULL_REQUEST_TEMPLATE      │
└─────────────────────────────────────────────┘
```

### エージェント → スキル → ポリシーの参照関係

```text
@agent-builder ──→ (既存エージェントのフォーマットを参照して新規生成)
               ──→ agent_docs/ (設計パターン・命名仕様・TDD・プロンプトガイド)

@dev-env-builder ──→ /dev-env-setup ──→ /ci-hygiene
                                    └──→ /dependabot-baseline
                 ──→ agent_docs/mcp-usage.md

@repo-guardian ──→ /repo-audit ──→ policies/repository-checklist.md
               └──→ /repo-apply-baseline

@code-reviewer ──→ /git-workflow

@git-operator ──→ /git-workflow
             ──→ CONTRIBUTING.md
             ──→ .github/PULL_REQUEST_TEMPLATE.md
             ──→ .github/ISSUE_TEMPLATE/ (bug_report.yml, feature_request.yml)

@docs-writer ──→ agent_docs/naming-and-format.md
             ──→ (直接ファイルを参照)
```

---

## 各コンポーネントの詳細

### Dev Container（`.devcontainer/`）

| ファイル | 役割 |
|---------|------|
| `devcontainer.json` | コンテナイメージ・Features・VS Code 拡張・起動コマンドを定義 |

現在は **言語非依存の Universal Image** を使用しています。
`@dev-env-builder` で言語固有のイメージに変更できます。

技術スタック確定後に追加される可能性があるファイル:

- `Dockerfile` — カスタムイメージが必要な場合
- `docker-compose.yml` — DB やキャッシュサービスが必要な場合

### カスタムエージェント（`.github/agents/`）

エージェント定義は Markdown ファイルで、以下の構造を持ちます:

````text
```chatagent
---
name: エージェント名
description: "説明"
tools:
  - search
  - editFiles
  - runInTerminal
  - fetch
---

# エージェントタイトル

## 行動原則
## チェックリスト
## 作業手順
## 禁止事項
```
````

| エージェント | ツール | 主な役割 |
|------------|--------|---------|
| `dev-env-builder` | search, editFiles, runInTerminal, fetch | 開発環境の対話的構築 |
| `repo-guardian` | search, editFiles, runInTerminal, fetch | リポジトリ監査・標準化 |
| `code-reviewer` | search, fetch | PR レビューコメント提案 |
| `docs-writer` | search, editFiles | ドキュメント更新提案 |
| `agent-builder` | search, editFiles, runInTerminal, fetch | カスタムエージェントの対話的設計・生成 |
| `git-operator` | search, runInTerminal | Git 運用（ブランチ・コミット・PR・Issue・hotfix/release） |

### スキル（`.github/skills/`）

スキルはエージェントが参照する手順書です。以下の構造を持ちます:

````text
```skill
---
name: スキル名
description: "説明"
---

# スキルタイトル

## 概要
## 手順テーブル / セクション
## テンプレート・コード例
```
````

| スキル | 行数 | 主な内容 |
|--------|------|---------|
| `dev-env-setup` | 約 630 行 | 5 言語の Dev Container・CI・Dependabot テンプレート |
| `repo-audit` | — | 監査チェックリストと手順 |
| `repo-apply-baseline` | — | 不足ファイル追加の優先度・テンプレート |
| `ci-hygiene` | — | 5 ツールの CI ワークフロー構成 |
| `dependabot-baseline` | — | エコシステム別 Dependabot 設定 |
| `git-workflow` | 約 250 行 | ブランチ・コミット・PR・rebase・hotfix・release |

### ポリシー（`.github/policies/`）

エージェントとスキルが準拠基準として参照するドキュメントです:

| ファイル | 内容 |
|---------|------|
| `repository-checklist.md` | 必須・推奨ファイルのチェックリスト |
| `ci-tools.md` | CI ツール（actionlint 等）の詳細仕様 |

### CI ワークフロー（`.github/workflows/`）

| ファイル | トリガー | ジョブ |
|---------|---------|--------|
| `ci.yml` | PR / push to main | actionlint, markdownlint, yamllint, gitleaks, typos |

すべて **言語非依存** の衛生チェックです。
言語固有のビルド・テストジョブは別途追加します。

### VS Code 設定（`.vscode/`）

| ファイル | 役割 |
|---------|------|
| `settings.json` | Copilot Hooks（postSave / postCommand）、エージェント設定 |
| `extensions.json` | 推奨拡張機能リスト |
| `mcp.json` | GitHub MCP Server（Docker 経由）の接続設定 |

### ドキュメント

| ディレクトリ | 対象読者 | 内容 |
|------------|---------|------|
| `human_docs/` | 人間の開発者 | 使い方・カスタマイズ手順・利用フロー |
| `agent_docs/` | AI エージェント | 自己参照用リファレンス・設計仕様・連携ルール |

`agent_docs/` は AI エージェントが `read_file` で自律的に取得するリファレンス集です。
エージェント間の参照関係・設計パターン・命名仕様・MCP 利用ガイド・TDD テンプレート・プロンプトベストプラクティスが含まれます。

### コミュニティヘルスファイル

GitHub が自動認識するファイル群です:

| ファイル | 役割 | カスタマイズ |
|---------|------|------------|
| `README.md` | プロジェクト概要 | 必須（TODO あり） |
| `CONTRIBUTING.md` | 開発参加手順 | 必須（URL・TODO） |
| `SECURITY.md` | 脆弱性報告導線 | 必須（URL・メール） |
| `LICENSE` | MIT ライセンス | 必須（年・著者名） |
| `CODE_OF_CONDUCT.md` | 行動規範 | 変更不要 |
| `CODEOWNERS` | コードオーナー | 必須（ユーザー名） |

---

## データフロー

### テンプレート利用時の典型的フロー

```text
1. テンプレートからリポジトリ作成
      │
      ▼
2. プロジェクト固有文字列を置換（手動 or sed）
      │
      ▼
3. @dev-env-builder でヒアリング
      │  ├─ 言語・バージョン
      │  ├─ フレームワーク
      │  └─ DB・サービス
      │
      ▼
4. ファイル自動生成
      │  ├─ devcontainer.json（更新）
      │  ├─ docker-compose.yml（新規、DB ありの場合）
      │  ├─ ci.yml（ジョブ追加）
      │  ├─ dependabot.yml（エコシステム追加）
      │  ├─ settings.json（Hooks 追加）
      │  └─ extensions.json（拡張追加）
      │
      ▼
5. @repo-guardian で監査・漏れチェック
      │
      ▼
6. @docs-writer でドキュメント整備
      │
      ▼
7. PR 作成 → CI 通過 → マージ
```
