"use client";
/** モーダル: ユーザープロフィールを編集する */

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { X, User, Upload, LogOut } from "lucide-react";
import { authApi } from "@/lib/api";
import { removeToken } from "@/lib/auth";
import { useChatStore } from "@/stores/chatStore";
import type { User as UserType } from "@/types";

interface Props {
  user: UserType;
  onClose: () => void;
  onUpdated: (user: UserType) => void;
}

export default function ProfileModal({ user, onClose, onUpdated }: Props) {
  const router = useRouter();
  const { setCurrentUser, setChannels, setCurrentChannel } = useChatStore();
  const [username, setUsername] = useState(user.username);
  const [avatarUrl, setAvatarUrl] = useState(user.avatar_url ?? "");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // オブジェクト URL のメモリリークを防ぐ
  useEffect(() => {
    return () => {
      if (avatarPreview) URL.revokeObjectURL(avatarPreview);
    };
  }, [avatarPreview]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (avatarPreview) URL.revokeObjectURL(avatarPreview);
    setAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setLoading(true);
    try {
      let updatedUser: UserType = user;

      if (avatarFile) {
        updatedUser = await authApi.uploadAvatar(avatarFile);
        setAvatarUrl(updatedUser.avatar_url ?? "");
      }

      const payload: { username?: string } = {};
      if (username.trim() && username.trim() !== user.username) {
        payload.username = username.trim();
      }
      if (Object.keys(payload).length > 0) {
        updatedUser = await authApi.updateMe(payload);
      }

      onUpdated(updatedUser);
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
  const previewSrc = avatarPreview ?? (avatarUrl || null);

  const handleLogout = () => {
    removeToken();
    setCurrentUser(null);
    setChannels([]);
    setCurrentChannel(null);
    onClose();
    router.push("/login");
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl rounded-2xl border border-white/50 dark:border-violet-500/20 shadow-2xl glow-surface w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold bg-gradient-to-r from-violet-600 to-fuchsia-500 bg-clip-text text-transparent">
            プロフィール設定
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* アバタープレビュー */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative">
            {previewSrc ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={previewSrc}
                alt="アバター"
                className="w-16 h-16 rounded-full object-cover border-2 border-violet-200 dark:border-violet-700/40 ring-2 ring-violet-500/10"
                onError={() => {
                  setAvatarUrl("");
                  setAvatarPreview(null);
                }}
              />
            ) : (
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-2xl font-bold shadow-lg glow-primary">
                {avatarLetter}
              </div>
            )}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="absolute bottom-0 right-0 bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white rounded-full p-1 hover:from-violet-600 hover:to-fuchsia-600 shadow-md transition-all"
              title="画像をアップロード"
            >
              <Upload size={12} />
            </button>
          </div>
          <div>
            <p className="font-medium text-gray-900 dark:text-gray-100">
              {displayName}
            </p>
            <p className="text-xs text-gray-400">{user.email}</p>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="text-xs text-violet-500 hover:text-fuchsia-600 mt-1 transition-colors"
            >
              画像を変更
            </button>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/gif,image/webp"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
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
              className="w-full bg-gray-50/80 dark:bg-gray-800/50 border border-gray-200/70 dark:border-gray-700/50 rounded-xl px-4 py-2.5 text-sm text-gray-900 dark:text-gray-100 outline-none focus:border-violet-400/60 dark:focus:border-violet-500/40 focus:ring-2 focus:ring-violet-500/20 transition-all duration-200"
            />
            <p className="text-xs text-gray-400 mt-1">
              未設定の場合はメールアドレスが表示名になります
            </p>
          </div>

          {error && <p className="text-xs text-red-500">{error}</p>}
          {success && <p className="text-xs text-green-500">更新しました！</p>}

          <div className="flex justify-between items-center pt-2">
            <button
              type="button"
              onClick={handleLogout}
              className="flex items-center gap-1 px-4 py-2 text-sm rounded-xl text-red-500 hover:bg-red-50/80 dark:hover:bg-red-900/20 transition-colors"
            >
              <LogOut size={14} />
              ログアウト
            </button>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-sm rounded-xl text-gray-600 dark:text-gray-300 hover:bg-gray-100/80 dark:hover:bg-gray-700/50 transition-colors"
              >
                キャンセル
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 text-sm rounded-xl bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 text-white font-medium shadow-lg glow-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {loading ? "保存中…" : "保存"}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
