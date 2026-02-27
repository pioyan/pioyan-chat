"use client";
/** Single message bubble. */

import { MessageSquare, Paperclip } from "lucide-react";
import type { Message } from "@/types";

interface Props {
  message: Message;
  onThreadClick: (messageId: string) => void;
}

export default function MessageItem({ message, onThreadClick }: Props) {
  const time = new Date(message.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  const displayName = message.sender_username;
  const avatarLetter = displayName[0]?.toUpperCase() ?? "?";

  return (
    <div className="group flex gap-3 px-4 py-1 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 rounded relative">
      {/* Avatar */}
      {message.sender_avatar_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={message.sender_avatar_url}
          alt={displayName}
          className="mt-1 shrink-0 w-8 h-8 rounded-full object-cover"
        />
      ) : (
        <div className="mt-1 shrink-0 w-8 h-8 rounded-full bg-violet-500 flex items-center justify-center text-white text-xs font-bold">
          {avatarLetter}
        </div>
      )}

      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-baseline gap-2">
          <span className="font-semibold text-sm text-zinc-900 dark:text-zinc-100">
            {displayName}
          </span>
          <span className="text-xs text-zinc-400">{time}</span>
        </div>

        {/* Content */}
        <p className="text-sm text-zinc-800 dark:text-zinc-200 whitespace-pre-wrap wrap-break-word">
          {message.content}
        </p>

        {/* File attachment */}
        {message.file_url && (
          <a
            href={message.file_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-violet-600 hover:underline mt-1"
          >
            <Paperclip size={12} />
            Attachment
          </a>
        )}

        {/* Thread button - existing replies */}
        {message.reply_count > 0 && (
          <button
            onClick={() => onThreadClick(message.id)}
            className="mt-1 flex items-center gap-1 text-xs text-violet-600 hover:underline"
          >
            <MessageSquare size={12} />
            {message.reply_count}{" "}
            {message.reply_count === 1 ? "reply" : "replies"}
          </button>
        )}
      </div>

      {/* Hover action - reply in thread */}
      {!message.thread_id && (
        <button
          onClick={() => onThreadClick(message.id)}
          className="absolute top-1 right-2 hidden group-hover:flex items-center gap-1 px-2 py-1 text-xs text-zinc-500 hover:text-violet-600 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded shadow-sm"
          aria-label="スレッドで返信"
        >
          <MessageSquare size={12} />
          <span>返信</span>
        </button>
      )}
    </div>
  );
}
