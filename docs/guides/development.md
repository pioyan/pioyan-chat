# 開発ワークフロー

pioyan-chat の開発プロセス・テスト・CI・コーディング規約をまとめています。

## 開発フロー

```text
1. PLAN.md でタスクを確認
      │
      ▼
2. feature ブランチ作成
      │  git checkout -b feat/my-feature
      │
      ▼
3. TDD サイクルで機能実装（t-wada 式 Red-Green-Refactor）
      │  ├─ Red:      テストを先に書く（pytest / Vitest）
      │  ├─ Green:    最小限の実装でテストを通す
      │  └─ Refactor: コードを整理する
      │
      ▼
4. ローカルで確認
      │  ├─ cd backend && pytest
      │  ├─ cd frontend && pnpm test
      │  └─ cd frontend && pnpm build
      │
      ▼
5. PR 作成 → CI 全ジョブ通過 → マージ
```

## ブランチ戦略

### ブランチ命名規則

`<type>/<short-description>` 形式で作成します。

| prefix | 用途 |
|--------|------|
| `feat/` | 新機能 |
| `fix/` | バグ修正 |
| `docs/` | ドキュメントのみの変更 |
| `refactor/` | リファクタリング |
| `ci/` | CI/CD の変更 |
| `chore/` | その他の雑務 |

### コミットメッセージ

[Conventional Commits](https://www.conventionalcommits.org/) に従います。

```text
<type>(<scope>): <subject>

<body>

<footer>
```

type: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `ci`, `chore`

## テスト

### バックエンド（pytest）

```bash
cd backend
pytest                     # 全テスト実行
pytest -v                  # 詳細出力
pytest tests/test_auth.py  # 特定テスト
pytest -x                  # 最初の失敗で停止
```

テストファイル:

| ファイル | テスト対象 |
|---------|----------|
| `test_auth.py` | 認証（signup / login / me） |
| `test_channels.py` | チャンネル CRUD + メンバー管理 |
| `test_messages.py` | メッセージ CRUD + 検索 + スレッド |
| `test_dm.py` | DM |
| `test_files.py` | ファイルアップロード |
| `test_bots.py` | ボット CRUD |
| `test_models.py` | Pydantic モデル |
| `test_validator.py` | Dockerfile バリデーター |

### フロントエンド（Vitest）

```bash
cd frontend
pnpm test          # run モード
pnpm test:watch    # watch モード
```

## Lint / Format

### バックエンド

```bash
cd backend
ruff check .       # lint
ruff format .      # フォーマット
```

### フロントエンド

```bash
cd frontend
pnpm lint          # ESLint
```

## CI（GitHub Actions）

PR 作成時に以下のジョブが自動実行されます。

### 言語非依存（衛生チェック）

| ジョブ | 内容 |
|--------|------|
| `actionlint` | GitHub Actions ワークフローの静的解析 |
| `markdownlint` | Markdown の品質チェック |
| `yamllint` | YAML の構文チェック |
| `gitleaks` | シークレット漏洩検知 |
| `typos` | 誤字検知 |

### バックエンド

| ジョブ | 内容 |
|--------|------|
| `backend-lint` | Ruff（lint + format check） |
| `backend-test` | pytest（Python 3.12 / 3.13 matrix、MongoDB サービスコンテナ付き） |

### フロントエンド

| ジョブ | 内容 |
|--------|------|
| `frontend-lint` | ESLint |
| `frontend-test` | Vitest |
| `frontend-build` | Next.js 本番ビルド検証 |

## PR ルール

1. PR テンプレートに従って変更内容を記述
2. CI のすべてのジョブが通過していること
3. セルフレビューを実施（`@code-reviewer` エージェントを活用）
4. ドキュメント更新が必要な場合は同時に対応

## Dependabot

依存関係の自動更新が設定されています。

| エコシステム | ディレクトリ |
|------------|------------|
| GitHub Actions | `.github/workflows/` |
| npm | `frontend/` |
| pip | `backend/` |
