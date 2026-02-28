# 次のステップ（2026-02-28 時点）

## 現在の状態サマリー

| 項目 | 状態 |
|------|------|
| Phase 0〜3 | **すべて完了** |
| Phase 4 | ほぼ完了（残り 1 項目） |
| フロントエンドテスト | 56 passed（7 ファイル） |
| バックエンドテスト | 193+ passed |
| パイプライン統合テスト | 9 passed |
| エラー耐性テスト | 20 passed |
| Socket.IO 検証テスト | 5 passed |
| 未コミット変更 | **19 modified + 26 untracked** ファイル |

### PLAN.md 未完了項目

```
- [ ] ボット実行エンジン（コンテナビルド + Copilot SDK 統合）
```

> Copilot SDK (`copilot-sdk`) が PyPI に存在しないためブロック中。  
> 現在はスタブモードで動作。

---

## タスク一覧（優先度順）

### 1. 未コミット変更のコミット & PR 作成 ⚠️ 最優先

**理由**: 50+ ファイルが未コミット。ロストリスクが高い。  
**対象ブランチ**: `feat/coding-bot-pipeline`（新規作成）

#### コミット分割案

| コミット | 内容 | ファイル数(目安) |
|---------|------|----------------|
| 1 | `feat(backend): add agent/coding-task models` | agent.py, agent_container.py, coding_task.py, channel.py 変更 |
| 2 | `feat(backend): add coding bot services` | services/ (container_service, github_service, mention_parser, orchestrator) |
| 3 | `feat(backend): add agent runtime` | agent_runtime/ |
| 4 | `feat(backend): add coding bot routers` | routers/ (agents, coding_channels, coding_tasks), sockets.py 変更 |
| 5 | `test(backend): add pipeline and resilience tests` | tests/ (全新規テストファイル) |
| 6 | `feat(frontend): add coding bot UI components` | AgentPanel, AgentMessageItem, CreateCodingChannelModal, MentionAutocomplete |
| 7 | `feat(frontend): add bot management panel` | BotManagementPanel, AppNavBar, Sidebar, page.tsx 変更 |
| 8 | `test(frontend): add bot management and socket.io tests` | BotManagementPanel.test.tsx, AgentPanel.socketio.test.tsx |
| 9 | `docs: add coding bot verification report` | docs/reports/coding-bot-verification.md, PLAN.md 更新 |

#### 手順

```bash
# 1. feature ブランチ作成
git checkout -b feat/coding-bot-pipeline

# 2. 上記の分割案に沿って段階的にコミット
# （各コミットで git add → git commit）

# 3. プッシュ & PR 作成
git push -u origin feat/coding-bot-pipeline
gh pr create --title "feat: AI coding bot pipeline (Phase 4)" \
  --body "Phase 4 のコーディングボットパイプライン全体を実装"
```

---

### 2. Playwright E2E テスト拡充

**理由**: 現在 `frontend/src/e2e/dm.spec.ts` のみ。コーディングチャンネルの UI フローが未テスト。  
**ブロッカー**: なし（スタブモードの API で検証可能）

#### テストシナリオ案

| テスト | 内容 |
|-------|------|
| コーディングチャンネル作成 | モーダル表示 → エージェント選択 → リポジトリ URL 入力 → 作成成功 |
| メンション送信 | `@bot-name タスク指示` → タスク作成 → ステータス表示 |
| Bot 管理パネル | ナビゲーション切替 → ボット一覧表示 → 登録フォーム |
| AgentPanel 表示 | コーディングチャンネル選択 → 右パネルにエージェント情報表示 |

#### 実装先

```
frontend/src/e2e/
├── dm.spec.ts                    # 既存
├── coding-channel.spec.ts        # 新規
├── bot-management.spec.ts        # 新規
└── agent-panel.spec.ts           # 新規
```

---

### 3. フロントエンド 新規コンポーネントの単体テスト補強

**理由**: 以下のコンポーネントに専用テストがない。

| コンポーネント | テスト有無 | 優先度 |
|--------------|----------|--------|
| `CreateCodingChannelModal` | ❌ なし | 高 |
| `MentionAutocomplete` | ❌ なし | 高 |
| `AgentMessageItem` | ❌ なし | 中 |
| `AgentPanel` | ⚠️ Socket.IO テストのみ | 中 |

#### テスト方針

- TDD（Red → Green → Refactor）で実装
- Vitest + React Testing Library
- モック: `@/lib/api` の API 関数、Socket.IO

---

### 4. Copilot SDK 代替設計

**理由**: `copilot-sdk` が PyPI に存在しないため Phase 4 の最終項目がブロック中。  
**アクション**: 代替アーキテクチャを検討・設計する。

#### 代替案

| 案 | 概要 | メリット | デメリット |
|---|------|---------|-----------|
| A | GitHub API + OpenAI API 直接統合 | SDK 不要、すぐ実装可能 | Copilot のコンテキスト理解が限定的 |
| B | GitHub Copilot CLI をコンテナ内で利用 | Copilot エコシステム活用 | CLI の自動化が複雑 |
| C | スタブモードを正式機能として維持 | 変更不要 | AI コーディング機能なし |
| D | Copilot SDK リリースを待つ | 本来の設計通り | 時期不明 |

#### 推奨

**案 A** を検討。Agent Runtime の `copilot_client.py` を OpenAI API 互換に書き換える設計書を作成し、実装可否を判断する。

---

### 5. Phase C: talent-flow アプリの本実装

**理由**: 検証レポート §9 の項目。ボットパイプラインを使って実際の開発タスクを実行する統合テスト。  
**前提**: タスク 4 の代替案実装後、または手動でパイプラインを駆動。

#### 検証項目

- [ ] talent-flow に Issue を作成
- [ ] pioyan-chat のコーディングチャンネルで `@agent Issue内容` を送信
- [ ] Agent がブランチ作成 → コード生成 → PR 作成を自動実行
- [ ] PR の内容をレビュー
- [ ] talent-flow のテストが CI で通過

---

### 6. ドキュメント更新

| ドキュメント | 更新内容 |
|------------|---------|
| `docs/reports/coding-bot-verification.md` | §9 の完了済み項目にチェックマークを追加 |
| `docs/guides/features.md` | Bot 管理 UI、コーディングチャンネル機能の記載 |
| `docs/reference/realtime.md` | `task_status` イベントの仕様追記 |
| `docs/reference/api-reference.md` | Agent / CodingTask / CodingChannel エンドポイント追記 |
| `README.md` | コーディングボット機能のセクション追加 |

---

## 推奨フロー

```
1. コミット & PR 作成        ← 今すぐ（データ保全）
2. E2E テスト拡充            ← PR マージ後
3. コンポーネントテスト補強    ← 並行可能
4. Copilot SDK 代替設計       ← 設計検討
5. talent-flow 本実装         ← 4 の結果次第
6. ドキュメント更新            ← 随時
```
