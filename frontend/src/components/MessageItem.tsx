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

  return (
    <div className="group flex gap-3 px-4 py-1 hover:bg-zinc-50 dark:hover:bg-zinc-800/50 rounded">
      {/* Avatar placeholder */}
      <div className="mt-1 flex-shrink-0 w-8 h-8 rounded-full bg-violet-500 flex items-center justify-center text-white text-xs font-bold">
        {message.sender_id.slice(0, 2).toUpperCase()}
      </div>

      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-baseline gap-2">
          <span className="font-semibold text-sm text-zinc-900 dark:text-zinc-100">
            {message.sender_id}
          </span>
          <span className="text-xs text-zinc-400">{time}</span>
        </div>

        {/* Content */}
        <p className="text-sm text-zinc-800 dark:text-zinc-200 whitespace-pre-wrap break-words">
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

        {/* Thread button */}
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
    </div>
  );
}
