# CI 推奨ツール一覧

組織標準の CI で使用する、言語非依存の衛生チェックツールをまとめます。

## 必須ツール

### actionlint

- **目的**: GitHub Actions ワークフローファイル (`.yml`) の静的解析
- **検出例**: 未定義の secrets 参照、不正な式構文、非推奨の構文
- **GitHub Action**: `reviewdog/action-actionlint@v1`
- **ローカル実行**: `brew install actionlint && actionlint`
- **公式**: https://github.com/rhysd/actionlint

### markdownlint-cli2

- **目的**: Markdown ファイルの品質・一貫性チェック
- **検出例**: 見出しレベルの飛び、行末スペース、リスト記法の不一致
- **GitHub Action**: `DavidAnson/markdownlint-cli2-action@v19`
- **ローカル実行**: `npx markdownlint-cli2 "**/*.md"`
- **設定ファイル**: `.markdownlint.yml`（カスタムルール用）
- **公式**: https://github.com/DavidAnson/markdownlint-cli2

### yamllint

- **目的**: YAML ファイルの構文・スタイルチェック
- **検出例**: インデント不整合、重複キー、行長超過
- **GitHub Action**: `ibiqlik/action-yamllint@v3`
- **ローカル実行**: `pip install yamllint && yamllint .`
- **設定ファイル**: `.yamllint.yml`（カスタムルール用）
- **公式**: https://github.com/adrienverge/yamllint

### gitleaks

- **目的**: Git 履歴・差分内のシークレット（API キー、パスワード等）漏洩検知
- **検出例**: AWS Access Key、GitHub Token、秘密鍵
- **GitHub Action**: `gitleaks/gitleaks-action@v2`
- **ローカル実行**: `brew install gitleaks && gitleaks detect`
- **設定ファイル**: `.gitleaks.toml`（許可リスト・カスタムルール用）
- **公式**: https://github.com/gitleaks/gitleaks

## 推奨ツール

### typos

- **目的**: ソースコード・ドキュメント内の誤字検知
- **検出例**: `teh` → `the`、`recieve` → `receive`
- **GitHub Action**: `crate-ci/typos@master`
- **ローカル実行**: `brew install typos-cli && typos`
- **設定ファイル**: `_typos.toml`（辞書・除外パターン用）
- **公式**: https://github.com/crate-ci/typos
- **備考**: 日本語リポジトリでは誤検知が多い場合があるため、段階導入を推奨

## ローカル開発での利用

これらのツールは CI だけでなく、ローカル開発環境でも実行できます。
VS Code の MCP 連携を使うことで、エージェントからも呼び出し可能です。

### 一括インストール（macOS）

```bash
brew install actionlint yamllint gitleaks typos-cli
npm install -g markdownlint-cli2
```

### 一括インストール（Ubuntu/Debian）

```bash
pip install yamllint
npm install -g markdownlint-cli2
# actionlint, gitleaks, typos は GitHub Releases からバイナリをダウンロード
```
