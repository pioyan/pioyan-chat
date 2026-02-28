"use client";
/**
 * ボット管理パネル: ボットの一覧表示・登録・削除を行う。
 * 既存の botsApi クライアントを使用。
 */

import {
  AlertCircle,
  Bot,
  FileCode2,
  Loader2,
  Plus,
  Trash2,
  X,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { botsApi } from "@/lib/api";
import type { Bot as BotType } from "@/types";

/** ステータスバッジの色マッピング */
const statusColors: Record<string, string> = {
  registered:
    "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 border-gray-200/60 dark:border-gray-700/40",
  building:
    "bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-200/60 dark:border-amber-700/40",
  ready:
    "bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 border-emerald-200/60 dark:border-emerald-700/40",
  error:
    "bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-200/60 dark:border-red-700/40",
};

export default function BotManagementPanel() {
  const [bots, setBots] = useState<BotType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  // ── Registration form state ──
  const [formName, setFormName] = useState("");
  const [formDesc, setFormDesc] = useState("");
  const [formFile, setFormFile] = useState<File | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadBots = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await botsApi.list();
      setBots(data);
    } catch {
      setError("ボット一覧の取得に失敗しました");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadBots();
  }, [loadBots]);

  // ── Registration ──────────────────────────────────────────
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);

    // Validation
    if (!formName.trim()) {
      setFormError("ボット名は必須です");
      return;
    }
    if (!formFile) {
      setFormError("コンテナファイルを選択してください");
      return;
    }

    setSubmitting(true);
    try {
      await botsApi.register(
        formName.trim(),
        formFile,
        formDesc.trim() || undefined,
      );
      // Reset form & refresh list
      setFormName("");
      setFormDesc("");
      setFormFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      setShowForm(false);
      await loadBots();
    } catch {
      setFormError("登録に失敗しました");
    } finally {
      setSubmitting(false);
    }
  };

  // ── Deletion ──────────────────────────────────────────────
  const handleDelete = async (bot: BotType) => {
    if (!window.confirm(`「${bot.name}」を削除しますか？`)) return;
    try {
      await botsApi.delete(bot.id);
      await loadBots();
    } catch {
      setError("削除に失敗しました");
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-white/95 dark:bg-gray-950/95">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200/50 dark:border-gray-700/30 bg-gradient-to-r from-cyan-50/30 to-violet-50/20 dark:from-cyan-950/10 dark:to-violet-950/5">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center shadow-md shadow-cyan-500/20">
            <Bot size={16} className="text-white" />
          </div>
          <h2 className="font-semibold text-lg bg-gradient-to-r from-cyan-600 to-violet-600 dark:from-cyan-400 dark:to-violet-400 bg-clip-text text-transparent">
            ボット管理
          </h2>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white hover:shadow-lg hover:shadow-violet-500/25 transition-all"
          aria-label="ボットを登録"
        >
          {showForm ? <X size={14} /> : <Plus size={14} />}
          {showForm ? "閉じる" : "ボットを登録"}
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mx-6 mt-4 flex items-center gap-2 px-4 py-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200/60 dark:border-red-700/40 text-red-600 dark:text-red-400 text-sm">
          <AlertCircle size={14} />
          {error}
        </div>
      )}

      {/* Registration form */}
      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="mx-6 mt-4 p-4 rounded-xl border border-cyan-200/50 dark:border-cyan-700/30 bg-cyan-50/30 dark:bg-cyan-950/10 space-y-3"
        >
          <div>
            <label
              htmlFor="bot-name"
              className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1"
            >
              ボット名
            </label>
            <input
              id="bot-name"
              type="text"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-violet-500/40"
              placeholder="例: build-bot"
              maxLength={100}
            />
          </div>
          <div>
            <label
              htmlFor="bot-desc"
              className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1"
            >
              説明
            </label>
            <input
              id="bot-desc"
              type="text"
              value={formDesc}
              onChange={(e) => setFormDesc(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 text-sm text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-violet-500/40"
              placeholder="ボットの説明（任意）"
              maxLength={500}
            />
          </div>
          <div>
            <label
              htmlFor="bot-file"
              className="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1"
            >
              コンテナファイル
            </label>
            <input
              id="bot-file"
              ref={fileInputRef}
              type="file"
              accept=".dockerfile,Dockerfile,Containerfile,*"
              onChange={(e) => setFormFile(e.target.files?.[0] ?? null)}
              className="w-full text-sm text-gray-600 dark:text-gray-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-violet-50 file:text-violet-600 dark:file:bg-violet-900/30 dark:file:text-violet-400 hover:file:bg-violet-100"
            />
          </div>

          {formError && (
            <div className="flex items-center gap-1.5 text-sm text-red-600 dark:text-red-400">
              <AlertCircle size={13} />
              {formError}
            </div>
          )}

          <div className="flex justify-end gap-2 pt-1">
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-3 py-1.5 rounded-lg text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              キャンセル
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-sm font-medium bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white disabled:opacity-50 hover:shadow-lg hover:shadow-violet-500/25 transition-all"
              aria-label="登録する"
            >
              {submitting && <Loader2 size={13} className="animate-spin" />}
              登録する
            </button>
          </div>
        </form>
      )}

      {/* Bot list */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 size={28} className="animate-spin text-violet-400" />
          </div>
        ) : bots.length === 0 ? (
          <div className="text-center py-16">
            <Bot
              size={48}
              className="mx-auto text-gray-200 dark:text-gray-700 mb-3"
            />
            <p className="text-sm text-gray-400 dark:text-gray-500">
              登録されたボットはありません
            </p>
            <p className="text-xs text-gray-400/70 dark:text-gray-600 mt-1">
              「ボットを登録」で最初のボットを追加しましょう
            </p>
          </div>
        ) : (
          <div className="grid gap-3">
            {bots.map((bot) => (
              <div
                key={bot.id}
                data-testid={`bot-card-${bot.id}`}
                className="flex items-start gap-3 p-4 rounded-xl border border-gray-200/60 dark:border-gray-700/30 bg-white dark:bg-gray-900/60 hover:shadow-lg hover:shadow-violet-500/5 transition-all group"
              >
                {/* Icon */}
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center text-white shrink-0 shadow-md">
                  <FileCode2 size={18} />
                </div>
                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-sm text-gray-900 dark:text-gray-100">
                      {bot.name}
                    </h3>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded-full border font-medium ${
                        statusColors[bot.status] ?? statusColors.registered
                      }`}
                    >
                      {bot.status}
                    </span>
                  </div>
                  {bot.description && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-2">
                      {bot.description}
                    </p>
                  )}
                  <div className="flex items-center gap-3 mt-1.5 text-[11px] text-gray-400">
                    <span className="font-mono">
                      {bot.container_file_name}
                    </span>
                    <span>
                      {new Date(bot.created_at).toLocaleDateString("ja-JP")}
                    </span>
                  </div>
                </div>
                {/* Actions */}
                <button
                  onClick={() => handleDelete(bot)}
                  className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all"
                  aria-label="削除"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
