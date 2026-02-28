"use client";
/** モーダル: コーディングチャンネルを作成する */

import { useState } from "react";
import { Code2, GitBranch, X } from "lucide-react";
import { codingChannelsApi } from "@/lib/api";
import type { Channel } from "@/types";

interface Props {
  onClose: () => void;
  onCreated: (channel: Channel) => void;
}

export default function CreateCodingChannelModal({
  onClose,
  onCreated,
}: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [defaultBranch, setDefaultBranch] = useState("main");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !repoUrl.trim()) return;

    setError(null);
    setLoading(true);
    try {
      const channel = await codingChannelsApi.create({
        name: name.trim(),
        description: description.trim() || undefined,
        repo_url: repoUrl.trim(),
        default_branch: defaultBranch.trim() || undefined,
      });
      onCreated(channel);
      onClose();
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? err.message
          : "コーディングチャンネルの作成に失敗しました",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl rounded-2xl border border-white/50 dark:border-cyan-500/20 shadow-2xl glow-surface w-full max-w-md overflow-hidden">
        {/* Cyan accent header banner */}
        <div className="bg-gradient-to-r from-cyan-500/10 to-violet-500/10 dark:from-cyan-900/20 dark:to-violet-900/20 px-6 pt-5 pb-4 border-b border-cyan-200/30 dark:border-cyan-700/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <Code2 size={18} className="text-white" />
              </div>
              <div>
                <h2 className="text-base font-bold bg-gradient-to-r from-cyan-600 to-violet-600 dark:from-cyan-400 dark:to-violet-400 bg-clip-text text-transparent">
                  コーディングチャンネルを作成
                </h2>
                <p className="text-[11px] text-gray-400">
                  GitHub リポジトリと AI エージェントを連携
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100/60 dark:hover:bg-gray-800/60 p-1"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* チャンネル名 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              チャンネル名 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="例: my-project"
              required
              maxLength={80}
              className="w-full bg-gray-50/80 dark:bg-gray-800/50 border border-gray-200/70 dark:border-gray-700/50 rounded-xl px-4 py-2.5 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 outline-none focus:border-violet-400/60 dark:focus:border-violet-500/40 focus:ring-2 focus:ring-violet-500/20 transition-all duration-200"
            />
          </div>

          {/* リポジトリ URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              GitHub リポジトリ URL <span className="text-red-500">*</span>
            </label>
            <input
              type="url"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/owner/repo"
              required
              className="w-full bg-gray-50/80 dark:bg-gray-800/50 border border-gray-200/70 dark:border-gray-700/50 rounded-xl px-4 py-2.5 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 outline-none focus:border-violet-400/60 dark:focus:border-violet-500/40 focus:ring-2 focus:ring-violet-500/20 transition-all duration-200"
            />
            <p className="mt-1 text-xs text-gray-400">
              https://github.com/owner/repo 形式
            </p>
          </div>

          {/* デフォルトブランチ */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              デフォルトブランチ
            </label>
            <div className="relative">
              <GitBranch
                size={14}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
              />
              <input
                type="text"
                value={defaultBranch}
                onChange={(e) => setDefaultBranch(e.target.value)}
                placeholder="main"
                maxLength={50}
                className="w-full pl-9 bg-gray-50/80 dark:bg-gray-800/50 border border-gray-200/70 dark:border-gray-700/50 rounded-xl px-4 py-2.5 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 outline-none focus:border-violet-400/60 dark:focus:border-violet-500/40 focus:ring-2 focus:ring-violet-500/20 transition-all duration-200"
              />
            </div>
          </div>

          {/* 説明 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              説明（任意）
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="プロジェクトの概要"
              maxLength={256}
              className="w-full bg-gray-50/80 dark:bg-gray-800/50 border border-gray-200/70 dark:border-gray-700/50 rounded-xl px-4 py-2.5 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 outline-none focus:border-violet-400/60 dark:focus:border-violet-500/40 focus:ring-2 focus:ring-violet-500/20 transition-all duration-200"
            />
          </div>

          {error && <p className="text-xs text-red-500">{error}</p>}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm rounded-xl text-gray-600 dark:text-gray-300 hover:bg-gray-100/80 dark:hover:bg-gray-700/50 transition-colors"
            >
              キャンセル
            </button>
            <button
              type="submit"
              disabled={loading || !name.trim() || !repoUrl.trim()}
              className="px-4 py-2 text-sm rounded-xl bg-gradient-to-r from-cyan-500 to-violet-500 hover:from-cyan-600 hover:to-violet-600 text-white font-medium shadow-lg shadow-cyan-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {loading ? "作成中…" : "作成"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
