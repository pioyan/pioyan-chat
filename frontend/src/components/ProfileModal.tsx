"use client";
/** モーダル: ユーザープロフィールを編集する */

import { useState } from "react";
import { X, User } from "lucide-react";
import { authApi } from "@/lib/api";
import type { User as UserType } from "@/types";

interface Props {
  user: UserType;
  onClose: () => void;
  onUpdated: (user: UserType) => void;
}

export default function ProfileModal({ user, onClose, onUpdated }: Props) {
  const [username, setUsername] = useState(user.username);
  const [avatarUrl, setAvatarUrl] = useState(user.avatar_url ?? "");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setLoading(true);
    try {
      const payload: { username?: string; avatar_url?: string } = {};
      if (username.trim() && username.trim() !== user.username) {
        payload.username = username.trim();
      }
      const trimmedAvatarUrl = avatarUrl.trim();
      if (trimmedAvatarUrl !== (user.avatar_url ?? "")) {
        payload.avatar_url = trimmedAvatarUrl || "";
      }
      const updated = await authApi.updateMe(payload);
      onUpdated(updated);
      setSuccess(true);
      setTimeout(onClose, 800);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "更新に失敗しました");
    } finally {
      setLoading(false);
    }
  };

  const displayName = user.username || user.email;
  const avatarLetter = displayName[0]?.toUpperCase() ?? "?";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-xl w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
            プロフィール設定
          </h2>
          <button
            onClick={onClose}
            className="text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
          >
            <X size={18} />
          </button>
        </div>

        {/* アバタープレビュー */}
        <div className="flex items-center gap-4 mb-6">
          {avatarUrl ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={avatarUrl}
              alt="アバター"
              className="w-16 h-16 rounded-full object-cover border-2 border-zinc-200 dark:border-zinc-700"
              onError={() => setAvatarUrl("")}
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-violet-600 flex items-center justify-center text-white text-2xl font-bold">
              {avatarLetter}
            </div>
          )}
          <div>
            <p className="font-medium text-zinc-900 dark:text-zinc-100">
              {displayName}
            </p>
            <p className="text-xs text-zinc-400">{user.email}</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
              <User size={13} className="inline mr-1" />
              表示名
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={user.email}
              minLength={2}
              maxLength={64}
              className="w-full border border-zinc-300 dark:border-zinc-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 outline-none focus:ring-2 focus:ring-violet-500"
            />
            <p className="text-xs text-zinc-400 mt-1">
              未設定の場合はメールアドレスが表示名になります
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1">
              プロフィール画像 URL（任意）
            </label>
            <input
              type="url"
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
              placeholder="https://example.com/avatar.png"
              className="w-full border border-zinc-300 dark:border-zinc-600 rounded-lg px-3 py-2 text-sm bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 outline-none focus:ring-2 focus:ring-violet-500"
            />
          </div>

          {error && <p className="text-xs text-red-500">{error}</p>}
          {success && <p className="text-xs text-green-500">更新しました！</p>}

          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm rounded-lg text-zinc-600 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-700"
            >
              キャンセル
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm rounded-lg bg-violet-600 text-white hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "保存中…" : "保存"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
