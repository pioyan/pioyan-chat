# pioyan-chat ドキュメント

pioyan-chat のシステムドキュメントです。  
アーキテクチャ・API・フロントエンド・バックエンドの設計情報をまとめています。

## はじめに

| ドキュメント | 内容 |
|---|---|
| [getting-started.md](getting-started.md) | セットアップ・開発サーバー起動手順 |

## ガイド (`guides/`)

開発者・利用者向けのガイドドキュメントです。

| ドキュメント | 内容 |
|---|---|
| [features.md](guides/features.md) | 機能一覧と使い方ガイド |
| [frontend-guide.md](guides/frontend-guide.md) | フロントエンド（Next.js）の構成・コンポーネント・状態管理 |
| [backend-guide.md](guides/backend-guide.md) | バックエンド（FastAPI）の構成・ルーター・認証 |
| [development.md](guides/development.md) | 開発ワークフロー・テスト・CI・コーディング規約 |

## リファレンス (`reference/`)

技術仕様・API・データモデルのリファレンスです。

| ドキュメント | 内容 |
|---|---|
| [architecture.md](reference/architecture.md) | システムアーキテクチャ・ディレクトリ構成・技術スタック |
| [api-reference.md](reference/api-reference.md) | REST API 全エンドポイントのリファレンス |
| [data-models.md](reference/data-models.md) | データモデル定義（User / Channel / Message / Bot） |
| [realtime.md](reference/realtime.md) | Socket.IO リアルタイム通信の設計・イベント仕様 |
| [configuration.md](reference/configuration.md) | 環境変数・Docker Compose・設定項目 |

## レポート (`reports/`)

検証レポート・ステータスドキュメントです。

| ドキュメント | 内容 |
|---|---|
| [coding-bot-verification.md](reports/coding-bot-verification.md) | AI コーディングボット パイプライン検証レポート |
| [next-steps.md](reports/next-steps.md) | 次のステップ・ロードマップ |

## ディレクトリ構成

```text
docs/
├── README.md                          # 本ファイル（ドキュメント索引）
├── getting-started.md                 # セットアップガイド
├── guides/                            # 開発・利用ガイド
│   ├── features.md                    #   機能一覧
│   ├── frontend-guide.md              #   フロントエンドガイド
│   ├── backend-guide.md               #   バックエンドガイド
│   └── development.md                 #   開発ワークフロー
├── reference/                         # 技術リファレンス
│   ├── architecture.md                #   システムアーキテクチャ
│   ├── api-reference.md               #   REST API リファレンス
│   ├── data-models.md                 #   データモデル定義
│   ├── realtime.md                    #   Socket.IO 仕様
│   └── configuration.md               #   環境設定
└── reports/                           # 検証・ステータス
    ├── coding-bot-verification.md     #   ボットパイプライン検証
    └── next-steps.md                  #   次のステップ
```

## クイックリンク

- [構築計画（PLAN.md）](../PLAN.md)
- [プロジェクト README](../README.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
