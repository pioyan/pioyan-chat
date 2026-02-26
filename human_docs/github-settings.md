# GitHub リポジトリ設定ガイド

このドキュメントでは、develop-base を使用したプロジェクトで推奨される GitHub リポジトリの設定について、初心者にもわかりやすく説明します。

## 目次

1. [基本設定](#基本設定)
2. [エージェントが自動設定する項目](#エージェントが自動設定する項目)
3. [推奨される手動設定](#推奨される手動設定)
4. [セキュリティ設定](#セキュリティ設定)

## 基本設定

### リポジトリの可視性

リポジトリ作成時に選択する項目です：

- **Public（公開）**: 誰でもコードを閲覧可能。オープンソースプロジェクト向け
- **Private（非公開）**: 許可されたユーザーのみアクセス可能。社内プロジェクトや開発中のコード向け

**設定場所**: リポジトリ作成時、または Settings > General > Danger Zone > Change visibility

### ブランチ設定

#### デフォルトブランチ

develop-base では `main` ブランチをデフォルトとして使用します。

**設定場所**: Settings > General > Default branch

#### ブランチ保護ルール

main ブランチを保護し、品質を維持するための重要な設定です。

**推奨設定**（Settings > Branches > Branch protection rules）:

1. **Require a pull request before merging**（マージ前にPRを必須にする）
   - ✅ 有効にする
   - Require approvals: 1 以上（レビュー必須）

2. **Require status checks to pass before merging**（CIの通過を必須にする）
   - ✅ 有効にする
   - エージェントが CI を設定後、以下のチェックを必須に設定:
     - `actionlint`
     - `markdownlint`
     - `yamllint`
     - `gitleaks`
     - `typos`

3. **Require conversation resolution before merging**（コメント解決を必須にする）
   - ✅ 有効にする（レビューコメントの対応漏れを防ぐ）

4. **Require linear history**（リニアな履歴を必須にする）
   - ✅ 推奨（マージコミットを防ぎ、履歴を綺麗に保つ）

5. **Do not allow bypassing the above settings**（管理者も従う）
   - ✅ 推奨（チーム全体で同じルールを適用）

**初心者向けTips**:

- ブランチ保護は、main ブランチに直接 push できなくする機能です
- 全ての変更は PR（Pull Request）経由で行うことで、レビューとテストを徹底できます
- CI（継続的インテグレーション）の通過を必須にすることで、バグの混入を防げます

## エージェントが自動設定する項目

develop-base のエージェントは、以下の GitHub 設定を自動的に追加・有効化します。

### @dev-env-builder が設定する項目

**起動方法**: Copilot Chat で `@dev-env-builder` を呼び出し

このエージェントは、技術スタックに応じた開発環境を対話的に構築します。

#### 自動作成されるファイル

| ファイル | 内容 | 説明 |
|---------|------|------|
| `.github/workflows/*.yml` | GitHub Actions ワークフロー | CI/CD パイプラインの定義 |
| `.github/dependabot.yml` | Dependabot 設定 | 依存関係の自動更新 |
| `.devcontainer/devcontainer.json` | Dev Container 設定 | 統一された開発環境 |
| `.vscode/settings.json` | VS Code 設定 | Copilot Hooks、linter 設定 |

#### 有効化される GitHub 機能

- **GitHub Actions**: CI ワークフローの実行
- **Dependabot**: 依存パッケージの脆弱性検知と自動更新PR作成
- **Secrets**: 必要に応じて環境変数の設定を案内

**初心者向けTips**:

- GitHub Actions は、コードが push されたときやPRが作成されたときに自動でテストやチェックを実行する機能です
- Dependabot は、使用しているライブラリに更新があると自動でPRを作成してくれます

### @repo-guardian が追加する項目

**起動方法**: Copilot Chat で `@repo-guardian` を呼び出し

このエージェントは、リポジトリのベストプラクティス準拠状況を監査し、不足分を自動追加します。

#### 自動作成されるファイル

| ファイル | 内容 | 説明 |
|---------|------|------|
| `README.md` | プロジェクト概要 | リポジトリの説明書 |
| `CONTRIBUTING.md` | 貢献ガイドライン | コントリビューター向け手順 |
| `CODE_OF_CONDUCT.md` | 行動規範 | コミュニティルール |
| `SECURITY.md` | セキュリティポリシー | 脆弱性報告手順 |
| `LICENSE` | ライセンス | コードの利用条件 |
| `.github/CODEOWNERS` | コードオーナー | ファイルごとのレビュアー自動割当 |
| `.github/ISSUE_TEMPLATE/` | Issue テンプレート | バグ報告・機能要望フォーム |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR テンプレート | PRの説明フォーム |

#### 有効化される機能

- **Issue テンプレート**: Issue 作成時にフォームが表示される
- **PR テンプレート**: PR 作成時にチェックリストが自動挿入される
- **CODEOWNERS**: 特定のファイルが変更されたとき、自動でレビュアーが割り当てられる

**初心者向けTips**:

- これらのファイルは「コミュニティヘルスファイル」と呼ばれ、GitHubがプロジェクトの品質指標として評価します
- リポジトリの Settings > Insights > Community でスコアを確認できます

### /ci-hygiene スキルが設定する項目

**起動方法**: Copilot Chat で `/ci-hygiene` を呼び出し

言語非依存の CI 衛生チェックを設定します。

#### 追加される CI ワークフロー

| ワークフロー | 実行内容 | 検出する問題 |
|------------|---------|-------------|
| `ci-hygiene.yml` | 統合衛生チェック | 文法エラー、シークレット漏洩、誤字 |
| actionlint | GitHub Actions の静的解析 | ワークフローの構文エラー |
| markdownlint | Markdown の品質チェック | ドキュメントの書式問題 |
| yamllint | YAML の構文チェック | 設定ファイルの構文エラー |
| gitleaks | シークレット漏洩検知 | 秘密情報のコミット |
| typos | 誤字検知 | ドキュメントやコメントの誤字 |

**初心者向けTips**:

- これらのチェックは PR ごとに自動実行されます
- 失敗すると PR ページに ❌ が表示されるので、エラーを修正してから再度 push します
- Actions タブで実行履歴と詳細ログを確認できます

### /dependabot-baseline スキルが設定する項目

**起動方法**: Copilot Chat で `/dependabot-baseline` を呼び出し

Dependabot を段階的に導入します。

#### `.github/dependabot.yml` の設定内容

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

**初心者向けTips**:

- Dependabot は毎週、使用中のライブラリやアクションの更新をチェックします
- 更新があると自動で PR が作成されるので、内容を確認してマージします
- Settings > Security > Dependabot で設定状況を確認できます

## 推奨される手動設定

エージェントでは設定できない項目で、手動での設定を推奨します。

### 1. リポジトリの基本情報

#### Settings > General

- **Description（説明）**: リポジトリの短い説明文を追加（検索に表示される）
- **Website**: プロジェクトのURLがあれば設定
- **Topics**: 技術タグを追加（例: `typescript`, `react`, `ci-cd`）
- **Discussions**: コミュニティ向けなら有効化

### 2. GitHub Actions の設定

#### Settings > Actions > General

- **Actions permissions**: 「Allow all actions and reusable workflows」を選択
- **Workflow permissions**:
  - 読み取り専用（デフォルト）を推奨
  - bot による PR 作成が必要な場合のみ「Read and write permissions」
- **Allow GitHub Actions to create and approve pull requests**: 必要に応じて有効化

**初心者向けTips**:

- Actions は最小権限で動作させるのがセキュリティのベストプラクティスです

### 3. Merge button の設定

#### Settings > General > Pull Requests

推奨設定:

- ✅ Allow squash merging（複数コミットを1つにまとめる）
- ✅ Allow rebase merging（履歴をリニアに保つ）
- ❌ Allow merge commits（マージコミットを作らない）
- ✅ Automatically delete head branches（マージ後にブランチ自動削除）

**初心者向けTips**:

- Squash merge は複数の作業コミットを1つの綺麗なコミットにまとめてマージします
- Rebase merge は履歴をまっすぐに保ちます
- 「Automatically delete head branches」を有効にすると、ブランチの掃除が不要になります

### 4. Pages（GitHub Pages）

#### Settings > Pages

ドキュメントサイトを公開したい場合:

- Source: 「GitHub Actions」を選択（柔軟性が高い）
- または: 「Deploy from a branch」で `gh-pages` ブランチを選択

### 5. Environments（環境）

#### Settings > Environments

本番環境へのデプロイがある場合:

- Environment を作成（例: `production`, `staging`）
- Protection rules を設定（承認者、待機時間）
- Environment secrets を設定（APIキー等）

## セキュリティ設定

### 1. Security & analysis

#### Settings > Security & analysis

| 設定 | 推奨 | 説明 |
|------|-----|------|
| Dependency graph | ✅ 有効 | 依存関係の可視化 |
| Dependabot alerts | ✅ 有効 | 脆弱性の自動検知 |
| Dependabot security updates | ✅ 有効 | 脆弱性修正の自動PR |
| Secret scanning | ✅ 有効（Public は必須） | 秘密情報の漏洩検知 |
| Code scanning (CodeQL) | ✅ 推奨 | コードの脆弱性スキャン |

**初心者向けTips**:

- これらは全て無料で使える GitHub のセキュリティ機能です
- 有効にしておくだけで、脆弱性を自動検知・通知してくれます

### 2. Secrets の管理

#### Settings > Secrets and variables > Actions

API キーや認証情報を安全に保存します。

**使い方**:

1. 「New repository secret」をクリック
2. Name に `API_KEY` などの名前を入力（大文字スネークケース推奨）
3. Secret に実際の値を入力
4. ワークフローで `${{ secrets.API_KEY }}` として参照

**重要**:

- ❌ Secrets をコードに直接書かない
- ❌ `.env` ファイルを git に含めない
- ✅ gitleaks で漏洩チェックを常に行う

### 3. Vulnerability alerts の確認

#### Security タブ > Dependabot alerts

定期的に確認し、以下の対応を取ります:

1. **Critical/High の脆弱性**: 即座に対応
2. **Medium**: 計画的に対応
3. **Low**: 優先度低め

Dependabot が自動で PR を作成している場合、内容を確認してマージします。

## 設定確認チェックリスト

初期設定が完了したら、以下を確認してください：

### 必須項目

- [ ] デフォルトブランチが `main` になっている
- [ ] ブランチ保護ルールが main に設定されている
- [ ] GitHub Actions が有効になっている
- [ ] Dependabot alerts が有効になっている
- [ ] `.github/workflows/` に CI ワークフローがある
- [ ] README.md にプロジェクト情報が記載されている

### 推奨項目

- [ ] Description と Topics が設定されている
- [ ] Merge button の設定を確認した
- [ ] CODEOWNERS が設定されている
- [ ] Issue/PR テンプレートが設置されている
- [ ] SECURITY.md が設置されている
- [ ] Secret scanning が有効になっている

### エージェントによる自動設定

- [ ] `@dev-env-builder` で開発環境を構築した
- [ ] `@repo-guardian` でベストプラクティスを監査した
- [ ] `/ci-hygiene` で CI を設定した
- [ ] `/dependabot-baseline` で Dependabot を設定した

## トラブルシューティング

### GitHub Actions が実行されない

**原因**: Actions の権限設定や、ワークフローファイルの構文エラー

**解決策**:

1. Settings > Actions > General で Actions が許可されているか確認
2. Actions タブで実行履歴とエラーログを確認
3. actionlint でワークフローファイルをチェック

### Dependabot の PR が作成されない

**原因**: `.github/dependabot.yml` の設定ミス、または対象ファイルが存在しない

**解決策**:

1. `.github/dependabot.yml` が正しい YAML 形式か確認
2. `package-ecosystem` が実際に使用中の技術スタックと一致しているか確認
3. Settings > Security > Dependabot で有効化されているか確認

### CI が常に失敗する

**原因**: コードの品質問題、または CI の設定ミス

**解決策**:

1. Actions タブで詳細なエラーログを確認
2. ローカルで linter を実行して問題を特定:

   ```bash
   # Markdown チェック
   docker run --rm -v "$PWD:/workdir" davidanson/markdownlint-cli2:latest "**/*.md"
   
   # YAML チェック
   yamllint .
   
   # シークレット検知
   docker run -v "$PWD:/path" zricethezav/gitleaks:latest detect --source="/path"
   ```

3. VS Code の Copilot Hooks が有効な場合、保存時に自動チェックされます

## さらに学ぶ

- [GitHub Docs - リポジトリの管理](https://docs.github.com/ja/repositories)
- [GitHub Actions のドキュメント](https://docs.github.com/ja/actions)
- [Dependabot のドキュメント](https://docs.github.com/ja/code-security/dependabot)
- [ブランチ保護ルール](https://docs.github.com/ja/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)

---

**関連ドキュメント**:

- [getting-started.md](getting-started.md) - プロジェクトの初期セットアップ
- [agent-guide.md](agent-guide.md) - エージェントの詳細な使い方
- [architecture.md](architecture.md) - リポジトリの構造
