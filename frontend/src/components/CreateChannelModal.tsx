"use client";
/** モーダル: 新しいチャンネルを作成する */

import { useState } from "react";
import { X } from "lucide-react";
import { channelsApi } from "@/lib/api";
import type { Channel } from "@/types";

interface Props {
  onClose: () => void;
  onCreated: (channel: Channel) => void;
}

export default function CreateChannelModal({ onClose, onCreated }: Props) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isPrivate, setIsPrivate] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setError(null);
    setLoading(true);
    try {
      const channel = await channelsApi.create({
        name: name.trim(),
        description: description.trim() || undefined,
        is_private: isPrivate,
      });
      onCreated(channel);
      onClose();
    } catch (err: unknown) {
      setError(
        err instanceof Error ? err.message : "チャンネルの作成に失敗しました",
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
      <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl rounded-2xl border border-white/50 dark:border-violet-500/20 shadow-2xl glow-surface w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold bg-gradient-to-r from-violet-600 to-fuchsia-500 bg-clip-text text-transparent">
            チャンネルを作成
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              チャンネル名 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="例: プロジェクト全体"
              required
              maxLength={80}
              className="w-full bg-gray-50/80 dark:bg-gray-800/50 border border-gray-200/70 dark:border-gray-700/50 rounded-xl px-4 py-2.5 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 outline-none focus:border-violet-400/60 dark:focus:border-violet-500/40 focus:ring-2 focus:ring-violet-500/20 transition-all duration-200"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              説明（任意）
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="このチャンネルの目的"
              maxLength={256}
              className="w-full bg-gray-50/80 dark:bg-gray-800/50 border border-gray-200/70 dark:border-gray-700/50 rounded-xl px-4 py-2.5 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 outline-none focus:border-violet-400/60 dark:focus:border-violet-500/40 focus:ring-2 focus:ring-violet-500/20 transition-all duration-200"
            />
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={isPrivate}
              onChange={(e) => setIsPrivate(e.target.checked)}
              className="rounded border-gray-300 dark:border-gray-600 text-violet-600 focus:ring-violet-500/30"
            />
            <span className="text-sm text-gray-700 dark:text-gray-300">
              プライベートチャンネルにする
            </span>
          </label>

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
              disabled={loading || !name.trim()}
              className="px-4 py-2 text-sm rounded-xl bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 text-white font-medium shadow-lg glow-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {loading ? "作成中…" : "作成"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
