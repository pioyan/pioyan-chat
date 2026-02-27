"use client";
/** Thread (reply) panel shown on the right side. */

import { X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { messagesApi } from "@/lib/api";
import { useChatStore } from "@/stores/chatStore";
import type { Message } from "@/types";
import MessageInput from "./MessageInput";
import MessageItem from "./MessageItem";

export default function ThreadPanel() {
  const { threadMessageId, setThreadMessageId, messages, incrementReplyCount } =
    useChatStore();
  const [replies, setReplies] = useState<Message[]>([]);

  const fetchReplies = useCallback(() => {
    if (!threadMessageId) return;
    messagesApi
      .getThread(threadMessageId)
      .then(setReplies)
      .catch(console.error);
  }, [threadMessageId]);

  useEffect(() => {
    fetchReplies();
  }, [fetchReplies]);

  // 親メッセージをストアから計算
  const allMessages = Object.values(messages).flat();
  const parent: Message | null = threadMessageId
    ? (allMessages.find((m) => m.id === threadMessageId) ?? null)
    : null;

  if (!threadMessageId) return null;

  return (
    <aside className="w-80 border-l border-zinc-200 dark:border-zinc-700 flex flex-col h-full bg-white dark:bg-zinc-900">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-200 dark:border-zinc-700">
        <h2 className="font-semibold text-sm text-zinc-900 dark:text-zinc-100">
          スレッド
        </h2>
        <button
          onClick={() => setThreadMessageId(null)}
          className="text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
          aria-label="閉じる"
        >
          <X size={16} />
        </button>
      </div>

      {/* Parent message */}
      {parent && (
        <div className="border-b border-zinc-200 dark:border-zinc-700 py-2">
          <MessageItem message={parent} onThreadClick={() => {}} />
        </div>
      )}

      {/* Reply count */}
      {replies.length > 0 && (
        <div className="px-4 py-2 text-xs text-zinc-500 border-b border-zinc-200 dark:border-zinc-700">
          {replies.length} {replies.length === 1 ? "件の返信" : "件の返信"}
        </div>
      )}

      {/* Replies */}
      <div className="flex-1 overflow-y-auto py-2">
        {replies.map((r) => (
          <MessageItem key={r.id} message={r} onThreadClick={() => {}} />
        ))}
      </div>

      {/* Input */}
      {threadMessageId && (
        <MessageInput
          channelId={parent?.channel_id ?? ""}
          threadId={threadMessageId}
          placeholder="スレッドに返信..."
          onSent={() => {
            fetchReplies();
            if (parent) {
              incrementReplyCount(parent.channel_id, threadMessageId);
            }
          }}
        />
      )}
    </aside>
  );
}
