# agent_docs — AI エージェント向けリファレンス

AI エージェントが**自律的に参照する**ためのリファレンスドキュメント集です。
エージェント定義（`.github/agents/`）やスキル（`.github/skills/`）から必要に応じて `read_file` で取得してください。

> **`human_docs/` との棲み分け**
>
> - `human_docs/` — 人間の開発者向け（使い方・カスタマイズ手順・利用フロー）
> - `agent_docs/` — AI エージェント向け（自己参照用リファレンス・設計仕様・連携ルール）

## ドキュメント一覧

| ファイル | 概要 | 主な参照元 |
|---------|------|-----------|
| [reference-map.md](reference-map.md) | エージェント・スキル・ポリシー間の依存関係マップ | 全エージェント共通 |
| [design-patterns.md](design-patterns.md) | エージェント設計の 3 パターン（読取専用型・対話生成型・監査修正型） | `@agent-builder` |
| [naming-and-format.md](naming-and-format.md) | ファイル命名・コードフェンス・構造の正規仕様 | `@agent-builder`, `@docs-writer` |
| [mcp-usage.md](mcp-usage.md) | GitHub MCP / Context7 MCP の用途・利用パターン | `@dev-env-builder`, `@repo-guardian` |
| [tdd-template.md](tdd-template.md) | TDD セクションの独立リファレンス（t-wada 式サイクル・言語別例） | `@agent-builder` |
| [prompt-engineering.md](prompt-engineering.md) | エージェント・スキル記述のプロンプトベストプラクティス集 | `@agent-builder` |
