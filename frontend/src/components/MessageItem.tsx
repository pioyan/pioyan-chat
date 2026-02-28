"use client";
/** Single message bubble. */

import { MessageSquare, Paperclip } from "lucide-react";
import type { Message } from "@/types";
import MarkdownContent from "@/components/MarkdownContent";

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
    <div className="group flex gap-3 px-4 py-2 rounded-lg hover:bg-violet-50/40 dark:hover:bg-violet-950/20 border-l-2 border-transparent hover:border-violet-300/50 transition-all duration-150 relative">
      {/* Avatar */}
      {message.sender_avatar_url ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={message.sender_avatar_url}
          alt={displayName}
          className="mt-1 shrink-0 w-8 h-8 rounded-full object-cover"
        />
      ) : (
        <div className="mt-1 shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-xs font-bold shadow-md ring-2 ring-white/10 dark:ring-gray-800/30">
          {avatarLetter}
        </div>
      )}

      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-baseline gap-2">
          <span className="font-semibold text-sm text-gray-900 dark:text-gray-100">
            {displayName}
          </span>
          <span className="text-xs text-gray-400">{time}</span>
        </div>

        {/* Content */}
        <MarkdownContent content={message.content} />

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
          className="absolute top-1 right-2 hidden group-hover:flex items-center gap-1 px-2.5 py-1.5 text-xs text-gray-500 hover:text-violet-600 bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm border border-violet-200/40 dark:border-violet-700/30 hover:border-violet-400/60 rounded-lg shadow-md transition-all duration-150"
          aria-label="スレッドで返信"
        >
          <MessageSquare size={12} />
          <span>返信</span>
        </button>
      )}
    </div>
  );
}
