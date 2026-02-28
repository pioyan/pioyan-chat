"use client";
/** Single message bubble. */

import { Download, FileIcon, MessageSquare } from "lucide-react";
import type { Message } from "@/types";
import MarkdownContent from "@/components/MarkdownContent";

interface Props {
  message: Message;
  onThreadClick: (messageId: string) => void;
  currentUserId?: string;
}

export default function MessageItem({ message, onThreadClick, currentUserId }: Props) {
  const time = new Date(message.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  const displayName = message.sender_username;
  const avatarLetter = displayName[0]?.toUpperCase() ?? "?";
  const isOwn = !!currentUserId && message.sender_id === currentUserId;

  return (
    <div
      className={`group flex gap-3 px-4 py-2 rounded-lg transition-all duration-150 relative ${
        isOwn
          ? "flex-row-reverse hover:bg-fuchsia-50/40 dark:hover:bg-fuchsia-950/20"
          : "hover:bg-violet-50/40 dark:hover:bg-violet-950/20 border-l-2 border-transparent hover:border-violet-300/50"
      }`}
    >
      {/* Avatar */}
      {message.sender_avatar_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={message.sender_avatar_url}
          alt={displayName}
          className="mt-1 shrink-0 w-8 h-8 rounded-full object-cover"
        />
      ) : (
        <div
          className={`mt-1 shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-md ring-2 ring-white/10 dark:ring-gray-800/30 ${
            isOwn
              ? "bg-gradient-to-br from-fuchsia-500 to-violet-600"
              : "bg-gradient-to-br from-violet-500 to-fuchsia-500"
          }`}
        >
          {avatarLetter}
        </div>
      )}

      <div className={`flex-1 min-w-0 ${isOwn ? "flex flex-col items-end" : ""}`}>
        {/* Header */}
        <div className={`flex items-baseline gap-2 ${isOwn ? "flex-row-reverse" : ""}`}>
          <span className="font-semibold text-sm text-gray-900 dark:text-gray-100">
            {displayName}
          </span>
          <span className="text-xs text-gray-400">{time}</span>
        </div>

        {/* Content bubble / File card */}
        {message.file_url ? (
          <div
            className={`mt-0.5 flex items-center gap-2 px-3 py-2 rounded-2xl border text-sm shadow-sm max-w-xs lg:max-w-md ${
              isOwn
                ? "rounded-tr-sm bg-gradient-to-br from-violet-500/10 to-fuchsia-500/10 border-violet-300/50 dark:border-violet-600/40"
                : "rounded-tl-sm bg-white/70 dark:bg-gray-800/60 border-gray-200/60 dark:border-gray-700/40"
            }`}
          >
            <FileIcon
              size={16}
              className={isOwn ? "text-violet-500 shrink-0" : "text-gray-400 shrink-0"}
            />
            <span
              className={`flex-1 truncate text-xs font-medium ${
                isOwn ? "text-violet-700 dark:text-violet-300" : "text-gray-700 dark:text-gray-200"
              }`}
              title={message.content}
            >
              {message.content}
            </span>
            <a
              href={message.file_url}
              download={message.content}
              className={`shrink-0 p-1 rounded-lg transition-colors ${
                isOwn
                  ? "text-violet-600 hover:bg-violet-100 dark:hover:bg-violet-900/30"
                  : "text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700/50"
              }`}
              title="ダウンロード"
              aria-label={`${message.content} をダウンロード`}
            >
              <Download size={14} />
            </a>
          </div>
        ) : isOwn ? (
          <div className="mt-0.5 px-3 py-2 rounded-2xl rounded-tr-sm bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white text-sm shadow-md max-w-xs lg:max-w-md break-words">
            <MarkdownContent content={message.content} ownMessage />
          </div>
        ) : (
          <MarkdownContent content={message.content} />
        )}

        {/* スレッド返信インジケーター */}
        {message.reply_count > 0 && (
          <button
            onClick={() => onThreadClick(message.id)}
            className={`
              mt-2 inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium
              border transition-all duration-150 group/thread
              ${isOwn
                ? "border-white/30 text-white/80 hover:text-white hover:border-white/60 hover:bg-white/10"
                : "border-violet-300/50 dark:border-violet-500/30 text-violet-600 dark:text-violet-400 hover:bg-violet-50 dark:hover:bg-violet-900/20 hover:border-violet-400/70"
              }
            `}
            aria-label="スレッドを表示"
          >
            <span className="flex items-center gap-1">
              {/* アイコンバッジ */}
              <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold
                ${isOwn ? "bg-white/20" : "bg-violet-100 dark:bg-violet-800/40"}`}
              >
                <MessageSquare size={9} />
              </span>
              <span>
                {message.reply_count}件の返信
              </span>
            </span>
            {/* ホバー時の矢印 */}
            <span className="opacity-0 group-hover/thread:opacity-100 transition-opacity text-[10px]">
              › スレッドを表示
            </span>
          </button>
        )}
      </div>

      {/* Hover action - reply in thread */}
      {!message.thread_id && (
        <button
          onClick={() => onThreadClick(message.id)}
          className={`absolute top-1 ${isOwn ? "left-2" : "right-2"} hidden group-hover:flex items-center gap-1 px-2.5 py-1.5 text-xs text-gray-500 hover:text-violet-600 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm border border-violet-200/40 dark:border-violet-700/30 hover:border-violet-400/60 rounded-lg shadow-md transition-all duration-150`}
          aria-label="スレッドで返信"
        >
          <MessageSquare size={12} />
          <span>返信</span>
        </button>
      )}
    </div>
  );
}
