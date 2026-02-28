"use client";
/** Text + file input bar. */

import { Paperclip, Send } from "lucide-react";
import { useRef, useState } from "react";
import { filesApi, messagesApi } from "@/lib/api";
import { useChatStore } from "@/stores/chatStore";

interface Props {
  channelId: string;
  threadId?: string;
  placeholder?: string;
  onSent?: () => void;
}

export default function MessageInput({
  channelId,
  threadId,
  placeholder,
  onSent,
}: Props) {
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const addMessage = useChatStore((s) => s.addMessage);

  const handleSend = async () => {
    const trimmed = text.trim();
    if (!trimmed || sending) return;
    setSending(true);
    try {
      if (threadId) {
        await messagesApi.postThread(threadId, { content: trimmed });
      } else {
        const msg = await messagesApi.post(channelId, { content: trimmed });
        addMessage(msg);
      }
      setText("");
      onSent?.();
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void handleSend();
    }
  };

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSending(true);
    try {
      const { file_url } = await filesApi.upload(file);
      const msg = await messagesApi.post(channelId, {
        content: file.name,
        file_url,
      });
      addMessage(msg);
    } finally {
      setSending(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <div className="border-t border-gray-200/50 dark:border-gray-700/30 px-4 py-3 bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm">
      <div className="flex items-end gap-2 bg-white/80 dark:bg-gray-800/60 border border-gray-200/70 dark:border-gray-700/40 rounded-xl px-3 py-2.5 input-glow transition-all duration-200">
        {/* File upload button */}
        <button
          type="button"
          onClick={() => fileRef.current?.click()}
          className="text-gray-400 hover:text-violet-500 transition-colors"
          aria-label="ファイル添付"
        >
          <Paperclip size={18} />
        </button>
        <input
          ref={fileRef}
          type="file"
          className="hidden"
          onChange={handleFile}
          aria-hidden="true"
        />

        {/* Textarea */}
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder ?? "メッセージを入力..."}
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 outline-none"
          aria-label="メッセージ"
        />

        {/* Send button */}
        <button
          type="button"
          onClick={() => void handleSend()}
          disabled={!text.trim() || sending}
          className="w-8 h-8 flex items-center justify-center bg-gradient-to-br from-violet-500 to-fuchsia-500 disabled:from-gray-300 disabled:to-gray-300 dark:disabled:from-gray-700 dark:disabled:to-gray-700 text-white rounded-lg shadow-md disabled:shadow-none hover:shadow-lg hover:scale-105 active:scale-95 transition-all duration-150 disabled:cursor-not-allowed"
          aria-label="送信"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
