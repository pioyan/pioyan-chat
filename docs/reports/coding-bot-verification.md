# AI コーディングボット — パイプライン検証レポート

**検証日**: 2026-02-28
**対象**: pioyan-chat Phase 4E パイプライン → pioyan/talent-flow リポジトリ
**検証者**: pioyan (自動検証)

## 1. 概要

pioyan-chat の AI コーディングボット機能（Phase 4E パイプライン）の E2E 動作検証を実施。
パイプライン全体のフロー（タスク受付→コンテナ起動→Agent Runtime→git操作→PR作成→クリーンアップ）が
正常に動作することを確認した。

## 2. 検証環境

| 項目 | 値 |
|------|-----|
| pioyan-chat バックエンド | FastAPI + Socket.IO (port 8000) |
| pioyan-chat フロントエンド | Next.js 15 (port 3000) |
| MongoDB | 7.x (Docker Compose) |
| Agent Base イメージ | pioyan-chat-agent-base:latest (Python 3.13-slim + gh CLI) |
| Agent Runtime モード | スタブモード（Copilot SDK なし） |
| Docker ネットワーク | pioyan-chat-agents |
| ターゲットリポジトリ | pioyan/talent-flow |

## 3. 発見された問題と修正

### 3.1 Dockerfile: `copilot-sdk` パッケージ不存在

**問題**: `pip install copilot-sdk` が PyPI に存在しないためイメージビルドが失敗する。
**修正**: Dockerfile から `copilot-sdk` を削除し、`httpx` のみインストール。Agent Runtime はスタブモードで動作。

**ファイル**: `backend/container_images/agent-base/Dockerfile`

### 3.2 GH_TOKEN 環境変数の未設定

**問題**: `create_container()` で `GITHUB_TOKEN` のみ設定していたが、`gh` CLI は `GH_TOKEN` を参照するため PR 作成が認証エラーになる。
**修正**: `GH_TOKEN` も環境変数に追加。

**ファイル**: `backend/app/services/container_service.py` (`create_container`)

### 3.3 バックエンド→コンテナ HTTP 通信の不達

**問題**: バックエンドは Docker ホスト上で動作し、`http://{container_name}:8080` で Agent Runtime にアクセスしようとしていたが、Docker DNS はコンテナ間のみ有効でホストからは解決できない。
**修正**: ポートマッピング方式に変更。`create_container` に `ports={'8080/tcp': None}` を追加し、起動後に割り当てられたホストポートを取得して `localhost:{port}` でアクセス。

**ファイル**:
- `backend/app/services/container_service.py` (新メソッド `_get_host_port`, `run_agent_container` を 3-tuple 返却に変更, `wait_for_ready`/`send_task` に `host_port` パラメータ追加)
- `backend/app/services/orchestrator.py` (`execute_task` を新シグネチャに対応)
- `backend/tests/test_pipeline_integration.py` (モック戻り値を 3-tuple に更新)

### 3.4 `httpx.RemoteProtocolError` のキャッチ漏れ

**問題**: `wait_for_ready` のポーリングが `ConnectError` と `TimeoutException` のみキャッチしていたが、コンテナ起動直後に `RemoteProtocolError: Server disconnected without sending a response` が発生し、キャッチされずに例外が伝播してタスクが即座に失敗。
**修正**: `wait_for_ready` の except 句に `RemoteProtocolError`, `ReadError`, `OSError` を追加。

**ファイル**: `backend/app/services/container_service.py` (`wait_for_ready`)

### 3.5 `git push` の upstream 未設定 + `gh pr create` の `--head` フラグ欠落

**問題**: `git push origin branch_name` では upstream tracking が設定されず、`gh pr create` がリモートブランチを検知できない（「you must first push the current branch to a remote, or use the --head flag」エラー）。
**修正**:
1. `push()` に `-u` フラグを追加
2. `create_pr()` に `--head` フラグと `_current_branch()` ヘルパーを追加

**ファイル**: `backend/agent_runtime/git_ops.py`

### 3.6 `asyncio.get_event_loop()` の DeprecationWarning

**問題**: `main.py` で `asyncio.get_event_loop().run_until_complete()` を使用しており、Python 3.13 で DeprecationWarning が出力される。
**修正**: `asyncio.run()` に変更。

**ファイル**: `backend/agent_runtime/main.py`

## 4. パイプライン検証結果

### 4.1 タスク実行ログ

| # | タスク内容 | 送信時刻 | 完了時刻 | 所要時間 | ステータス | PR |
|---|-----------|---------|---------|---------|-----------|-----|
| 1 | 基盤タスク (1回目) | 12:31:32 | 12:31:33 | ~1秒 | **failed** | — |
| 2 | 基盤タスク (2回目, fix1適用後) | 12:33:25 | 12:33:26 | ~1秒 | **failed** | — |
| 3 | 簡易 README 作成 (fix2-5適用後) | 12:50:30 | 12:50:35 | **~5秒** | **completed** | [PR #2](https://github.com/pioyan/talent-flow/pull/2) |
| 4 | フル基盤セットアップ (全修正適用) | 12:54:53 | 12:54:58 | **~5秒** | **completed** | [PR #3](https://github.com/pioyan/talent-flow/pull/3) |

### 4.2 パイプラインフロー確認

| ステップ | 動作 | 結果 |
|---------|------|------|
| タスク受付 | POST /api/channels/{id}/tasks → pending | Pass |
| BackgroundTask 起動 | Orchestrator.execute_task() | Pass |
| ステータス更新 (running) | DB + Socket.IO 通知 | Pass |
| Agent Base イメージ存在確認 | docker.images.get() | Pass |
| コンテナ作成・起動 | docker.containers.create() + start() | Pass |
| ポートマッピング取得 | container.attrs → HostPort | Pass |
| ヘルスチェック | GET http://localhost:{port}/health → 200 | Pass |
| タスク送信 | POST http://localhost:{port}/task | Pass |
| git clone | HTTPS + token | Pass |
| git branch | checkout -b agent/{id}/{task_id} | Pass |
| スタブ実行 | AGENT_OUTPUT.md 生成 | Pass |
| git commit | git add -A + commit | Pass |
| git push | git push -u origin {branch} | Pass |
| PR 作成 | gh pr create --head {branch} | Pass |
| ステータス更新 (completed) | DB + Socket.IO 通知 | Pass |
| コンテナクリーンアップ | stop + remove | Pass |

## 5. 4観点スコアリング (Phase D-2)

| # | 評価観点 | 結果 | 備考 |
|---|---------|------|------|
| 1 | パイプライン動作 | **Pass** | 全フロー正常完了 |
| 2 | エラーハンドリング | **Pass** | 失敗時に failed ステータス + 明確なエラーメッセージ |
| 3 | コンテナ管理 | **Pass** | 起動・通信・クリーンアップ全て正常 |
| 4 | Git/GitHub 連携 | **Pass** | clone → push → PR 作成まで完了 |

> **注記**: 現時点ではスタブモード（Copilot SDK なし）のため、実際のコード生成は `AGENT_OUTPUT.md` のみ。
> Copilot SDK が利用可能になった時点で実コード生成の検証が必要。

## 6. パフォーマンスメトリクス

| メトリクス | 値 |
|-----------|-----|
| コンテナ起動→ヘルスチェック成功 | ~2-3 秒 |
| タスク送信→完了 (スタブ) | ~3-5 秒 |
| 総パイプライン時間 (pending→completed) | ~5 秒 |
| Docker イメージビルド (初回) | ~25 秒 |
| Docker イメージビルド (キャッシュ) | ~0.3 秒 |

## 7. テスト結果

| テストスイート | 結果 |
|--------------|------|
| バックエンド全体 | **193 passed** |
| パイプライン統合テスト | **9 passed** |
| Agent Runtime テスト | **10 passed** |
| フロントエンド | **0 tests** (テストファイルなし) |

## 8. 実装変更サマリー

### 変更ファイル一覧

| ファイル | 変更内容 |
|---------|---------|
| `backend/container_images/agent-base/Dockerfile` | `copilot-sdk` を削除 |
| `backend/app/services/container_service.py` | GH_TOKEN 追加, ポートマッピング, RemoteProtocolError キャッチ, `_get_host_port()` 追加 |
| `backend/app/services/orchestrator.py` | `host_port` パラメータ対応 |
| `backend/agent_runtime/git_ops.py` | `push -u`, `--head` フラグ, `_current_branch()` 追加 |
| `backend/agent_runtime/main.py` | `asyncio.run()` に更新 |
| `backend/tests/test_pipeline_integration.py` | 3-tuple モック, `host_port` アサーション |

## 9. 次のステップ

1. **Copilot SDK 統合**: スタブモードから実 SDK モードへの移行
2. **Phase C**: talent-flow アプリ本体の全機能実装（ボット経由）
3. **エラー耐性テスト (Phase D-3)**: 不正リポジトリURL, Docker停止, 不正トークン, タイムアウト
4. **Socket.IO リアルタイム通知**: フロントエンド AgentPanel でのステータス表示検証
