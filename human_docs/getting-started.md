# クイックスタート

develop-base テンプレートから新しいプロジェクトを作成する手順です。

## 前提条件

- [VS Code](https://code.visualstudio.com/) + [Dev Containers 拡張](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [Docker](https://www.docker.com/)
- [GitHub CLI](https://cli.github.com/)（`gh` コマンド）

## Step 1: テンプレートからリポジトリを作成

GitHub の **Use this template** ボタン、または `gh` コマンドでリポジトリを作成します。

```bash
gh repo create <owner>/<new-repo-name> \
  --template pioyan/develop-base \
  --private \
  --clone
cd <new-repo-name>
```

## Step 2: Dev Container で開発環境を起動

1. VS Code でリポジトリのフォルダを開く
2. コマンドパレット → **Dev Containers: Reopen in Container** を実行
3. コンテナ起動後、ターミナルで認証:

```bash
gh auth login
```

## Step 3: プロジェクト情報を書き換える

最低限、以下の **プロジェクト固有の文字列** を置換してください。
詳細は [customization-guide.md](customization-guide.md) を参照。

| 置換対象 | 置換先 | 対象ファイル |
|---------|--------|-------------|
| `sample-app` | あなたのプロジェクト名 | `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `.github/copilot-instructions.md`, `.github/ISSUE_TEMPLATE/config.yml` |
| `pioyan` | あなたの GitHub ユーザー名 / 組織名 | `LICENSE`, `.github/CODEOWNERS`, `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `.github/copilot-instructions.md`, `.github/ISSUE_TEMPLATE/config.yml` |
| `pioyan/sample-app` | `<owner>/<repo>` 形式のリポジトリパス | `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `.github/ISSUE_TEMPLATE/config.yml` |
| `security@example.com` | セキュリティ報告先メールアドレス | `SECURITY.md` |
| `develop-base` | プロジェクト名 | `.devcontainer/devcontainer.json` |

### 一括置換コマンド（参考）

```bash
# プロジェクト名の置換
grep -rl "sample-app" --include="*.md" --include="*.yml" --include="*.json" . \
  | xargs sed -i 's/sample-app/<your-project>/g'

# オーナー名の置換
grep -rl "pioyan" --include="*.md" --include="*.yml" --include="*.json" . \
  | xargs sed -i 's/pioyan/<your-owner>/g'
```

> **注意**: 一括置換後は必ず `git diff` で意図しない変更がないか確認してください。

## Step 4: 技術スタックに合わせた開発環境を構築

Copilot Chat で `@dev-env-builder` エージェントを呼び出し、
対話形式で開発環境を構築します。

```text
@dev-env-builder Node.js 22 + Next.js の開発環境を作成してください
```

エージェントが以下のファイルを自動生成・更新します:

- `.devcontainer/devcontainer.json`
- `.github/workflows/ci.yml`
- `.github/dependabot.yml`
- `.vscode/settings.json`
- `.vscode/extensions.json`

詳細は [agent-guide.md](agent-guide.md) を参照。

## Step 5: TODO コメントを埋める

テンプレートには `<!-- TODO: ... -->` が残っています。
以下のファイルの TODO を確認し、プロジェクト固有の情報を記入してください。

```bash
# TODO コメントの一覧を確認
grep -rn "TODO" --include="*.md" .
```

| ファイル | TODO 内容 |
|---------|----------|
| `README.md` | プロジェクト説明・前提条件・インストールコマンド・起動コマンド・使い方 |
| `SECURITY.md` | セキュリティ連絡先メール・サポートバージョンの表 |
| `CONTRIBUTING.md` | プロジェクト固有のコーディング規約 |
| `.github/copilot-instructions.md` | ビルド・テストコマンド |

## Step 6: 動作確認

```bash
# CI の衛生チェックをローカルで実行
npx markdownlint-cli2 "**/*.md"
yamllint .github/

# GitHub に push して CI を確認
git add -A
git commit -m "chore: initialize project from develop-base template"
git push origin main
```

## 次のステップ

- [customization-guide.md](customization-guide.md) — より詳細なカスタマイズが必要な場合
- [agent-guide.md](agent-guide.md) — AI エージェントを活用した開発フロー
- [architecture.md](architecture.md) — リポジトリ構成の全体像を理解する
