# エージェント活用ガイド

develop-base に組み込まれたカスタムエージェントとスキルの使い方を説明します。

## エージェントとは

カスタムエージェントは、VS Code の Copilot Chat で `@エージェント名` と呼び出すことで
利用できる専門 AI アシスタントです。
それぞれ特定のタスクに特化した知識と手順を持っています。

---

## カスタムエージェント一覧

### `@dev-env-builder` — 開発環境構築

**いつ使う？**
新しいプロジェクトの開発環境を一から作りたいとき。

**何をしてくれる？**
対話形式で言語・フレームワーク・DB 等をヒアリングし、
以下のファイルを自動生成・更新します:

- Dev Container 設定（`devcontainer.json`、必要に応じて `Dockerfile` / `docker-compose.yml`）
- CI ワークフロー（言語固有のビルド・テストジョブ追加）
- Dependabot 設定（言語エコシステム追加）
- VS Code 設定（拡張機能・linter・formatter）
- ドキュメント更新（README・copilot-instructions）

**使い方の例:**

```text
@dev-env-builder Python 3.13 + FastAPI + PostgreSQL の開発環境を作成してください
```

```text
@dev-env-builder Node.js 22 で pnpm を使いたいです。テストは Vitest、リンターは ESLint を使います
```

```text
@dev-env-builder Go 1.23 のシンプルな環境をセットアップしてください
```

**ヒアリングされる項目:**

| 区分 | 項目 | 例 |
|------|------|-----|
| 必須 | プログラミング言語 | Node.js / Python / Go / Rust / Java |
| 必須 | 言語バージョン | Node.js 22 / Python 3.13 |
| 必須 | パッケージマネージャ | npm / pnpm / poetry / cargo |
| 任意 | フレームワーク | Next.js / FastAPI / Gin |
| 任意 | データベース | PostgreSQL / MySQL |
| 任意 | キャッシュ等 | Redis / RabbitMQ |
| 任意 | テストフレームワーク | Jest / pytest |
| 任意 | リンター・フォーマッター | ESLint / Ruff |

> **ヒント**: 最初のメッセージに必要な情報をすべて含めると、
> ヒアリングのやり取りを省略してすぐに環境構築が始まります。

---

### `@repo-guardian` — リポジトリ標準化

**いつ使う？**

- テンプレートから作成した後、設定漏れがないか確認したいとき
- リポジトリのベストプラクティス準拠状況を監査したいとき
- 不足ファイルを自動追加して PR にしたいとき

**何をしてくれる？**

1. リポジトリの全体を監査し、不足ファイルを検出
2. 優先度順（セキュリティ → テンプレート → 推奨）に不足分を追加
3. 変更を PR としてまとめる

**使い方の例:**

```text
@repo-guardian このリポジトリのベストプラクティス準拠状況を確認してください
```

```text
@repo-guardian 不足しているファイルを追加する PR を作成してください
```

---

### `@code-reviewer` — コードレビュー

**いつ使う？**

- PR を出す前にセルフレビューしたいとき
- レビューコメントの草案を作りたいとき

**何をしてくれる？**
PR の差分を読み、以下の観点でレビューコメントを提案します:

| 観点 | チェック内容 |
|------|------------|
| セキュリティ | ハードコードされたシークレット、SQL インジェクション等 |
| コード品質 | 命名、複雑度、重複、エラーハンドリング |
| テスト | テストの追加・更新が適切か |
| ドキュメント | 公開 API の変更に対するドキュメント更新 |
| Git 運用 | Conventional Commits 準拠、ブランチ命名 |

**使い方の例:**

```text
@code-reviewer 現在の PR をレビューしてください
```

**出力形式:**

- 🔴 **要対応** — 修正が必要な問題
- 🟡 **改善推奨** — 品質向上のための提案
- 🟢 **良い点** — 評価できるポイント

---

### `@docs-writer` — ドキュメント更新

**いつ使う？**

- コードを変更した後、ドキュメントの更新が必要か確認したいとき
- ドキュメントの更新内容を自動生成したいとき

**何をしてくれる？**
コード変更を解析し、以下のドキュメントの更新提案を生成します:

- `README.md`
- `CONTRIBUTING.md`
- `.github/copilot-instructions.md`
- `.github/skills/*/SKILL.md`
- `.github/policies/*.md`

**使い方の例:**

```text
@docs-writer 最近のコード変更に合わせてドキュメントを更新してください
```

```text
@docs-writer README にセットアップ手順を追記してください
```

---

### `@git-operator` — Git 運用

**いつ使う？**

- ブランチの作成・切替・削除を規約に沿って行いたいとき
- Conventional Commits 形式でコミットしたいとき
- rebase・PR 作成・hotfix・release フローを実行したいとき
- Issue（バグ報告・機能要望）をテンプレートに沿って作成したいとき

**何をしてくれる？**

Git の運用全般をリポジトリ規約に沿って実行します:

| カテゴリ | 操作例 |
|---------|--------|
| ブランチ管理 | 作成・切替・削除・一覧表示 |
| コミット | Conventional Commits 形式・・amend・revert |
| Rebase | main の取り込み・interactive rebase |
| PR | テンプレートを使用した PR 作成・ステータス確認 |
| Issue | バグ報告・機能要望テンプレートに沿った Issue 作成 |
| Hotfix | 緊急修正ブランチの作成からマージまで |
| Release | release ブランチ・タグ付け・GitHub Release 作成 |

**使い方の例:**

```text
@git-operator feat/add-login-page ブランチを作成してください
```

```text
@git-operator 現在の変更を Conventional Commits 形式でコミットしてください
```

```text
@git-operator main の最新を取り込んで rebase してください
```

```text
@git-operator この変更を PR にしてください
```

```text
@git-operator ログインページが表示されないバグを Issue として報告してください
```

```text
@git-operator v1.2.0 のリリースフローを実行してください
```

> **安全性**: 破壊的な操作（force-push・reset --hard・ブランチ削除等）は必ず実行前に確認が入ります。

---

### `@agent-builder` — カスタムエージェント作成

**いつ使う？**

- プロジェクト固有のタスクに特化したカスタムエージェントを作りたいとき
- コード実装エージェントに TDD サイクルを組み込みたいとき
- エージェントの定義ファイルや関連スキルを自動生成したいとき

**何をしてくれる？**

1. 対話形式でエージェントの役割・ドメイン・ツールをヒアリング
2. エージェント定義を設計・提案し、ユーザーの承認を得る
3. `.github/agents/<name>.md` を既存規約に沿って生成
4. 必要に応じて `.github/skills/<name>/SKILL.md` も生成
5. コード実装エージェントには t-wada 式 TDD（Red→Green→Refactor）サイクルを自動組み込み
6. 関連ドキュメント（copilot-instructions・agent-guide・architecture）を更新

**使い方の例:**

```text
@agent-builder TypeScript のバックエンド API を実装するエージェントを作ってください
```

```text
@agent-builder React コンポーネントを TDD で実装するフロントエンドエージェントを作成してください
```

```text
@agent-builder インフラ構成をレビューするエージェントを作りたいです
```

**対話フロー:**

```text
1. ヒアリング（役割・ドメイン・ツール・技術スタック）
2. 設計提案（エージェント定義のプレビューを提示）
3. ユーザー承認（修正フィードバック可）
4. ファイル生成（エージェント + スキル + ドキュメント更新）
```

> **TDD の自動判定**: エージェントがコード実装を行う場合は TDD セクションが自動組み込まれます。
> 監査・レビュー・ドキュメント系のエージェントでは省略されます。

---

## Agent Skills 一覧

スキルはエージェント内部で参照される手順書です。
Copilot Chat で `/スキル名` として直接呼び出すこともできます。

| スキル | 内容 | 主な利用場面 |
|--------|------|------------|
| `/dev-env-setup` | 言語別の Dev Container・CI・Dependabot テンプレート集 | `@dev-env-builder` が参照 |
| `/repo-audit` | リポジトリのベストプラクティス監査手順 | `@repo-guardian` が参照 |
| `/repo-apply-baseline` | 不足ファイルの追加手順とテンプレート | `@repo-guardian` が参照 |
| `/ci-hygiene` | CI 衛生チェック（actionlint 等）の導入手順 | CI 初期導入時 |
| `/dependabot-baseline` | Dependabot の段階的導入手順 | 依存管理の自動化時 |
| `/git-workflow` | ブランチ・コミット・PR・rebase の標準手順 | `@code-reviewer`, `@git-operator` が参照 |

---

## おすすめの利用フロー

### 新規プロジェクト立ち上げ時

```text
1. テンプレートからリポジトリを作成
2. @dev-env-builder で開発環境を構築
3. @agent-builder でプロジェクト固有のエージェントを作成
4. @repo-guardian で設定漏れを確認
5. @docs-writer でドキュメントを整備
```

### 日常の開発サイクル

```text
1. feature ブランチで実装（/git-workflow 参照）
2. @code-reviewer でセルフレビュー
3. @docs-writer でドキュメント更新を確認
4. PR を作成し、CI 通過を確認
```

### リポジトリの健全性チェック

```text
1. @repo-guardian で定期的に監査を実施
2. 不足分の PR を自動生成
3. dependabot.yml の更新状況を確認
```

---

## サブエージェント連携

`.vscode/settings.json` で `chat.customAgentInSubagent.enabled: true` が
設定されているため、メインの Copilot Chat からカスタムエージェントを
サブエージェントとして呼び出すことができます。

例えば、通常の Copilot Chat で以下のように指示すると、
適切なエージェントが自動的に呼び出されます:

```text
このリポジトリの開発環境を構築して、その後ドキュメントも更新してほしい
```

---

## Copilot Hooks（自動品質チェック）

エージェントがコードを生成・編集するたびに、以下のチェックが自動実行されます:

| タイミング | 対象ファイル | 実行コマンド |
|-----------|------------|------------|
| ファイル保存後 | `*.md` | markdownlint |
| ファイル保存後 | `*.yml` / `*.yaml` | yamllint |
| コマンド実行後 | 全ファイル | typos（誤字検知） |

手動で lint を実行する必要はありません。

---

## エージェント向けリファレンス（`agent_docs/`）

`agent_docs/` ディレクトリには、AI エージェントが自律的に参照するためのリファレンスが格納されています。
エージェントは必要に応じてこれらのドキュメントを `read_file` で取得し、設計判断や作業の精度を向上させます。

| ファイル | 概要 |
|---------|------|
| `reference-map.md` | エージェント・スキル・ポリシー間の依存関係マップ |
| `design-patterns.md` | エージェント設計の 3 パターン |
| `naming-and-format.md` | ファイル命名・コードフェンス・構造の正規仕様 |
| `mcp-usage.md` | GitHub MCP / Context7 MCP の利用パターン |
| `tdd-template.md` | TDD セクションの独立リファレンス |
| `prompt-engineering.md` | プロンプトベストプラクティス集 |

> **`human_docs/` との違い**: `human_docs/` は人間の開発者向け、`agent_docs/` は AI エージェントの自己参照用です。
