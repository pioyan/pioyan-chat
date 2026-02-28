"use client";
/** Scrollable message list for a channel. */

import { useEffect, useRef } from "react";
import type { Message } from "@/types";
import { useChatStore } from "@/stores/chatStore";
import MessageItem from "./MessageItem";

interface Props {
  messages: Message[];
  onThreadClick: (messageId: string) => void;
}

export default function MessageList({ messages, onThreadClick }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const currentUser = useChatStore((s) => s.currentUser);

  // 最新メッセージへ自動スクロール
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
        メッセージはまだありません
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto py-2">
      {messages.map((msg) => (
        <MessageItem
          key={msg.id}
          message={msg}
          onThreadClick={onThreadClick}
          currentUserId={currentUser?.id}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
