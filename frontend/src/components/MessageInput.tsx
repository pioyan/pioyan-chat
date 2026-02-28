"use client";
/** Text + file input bar with @mention autocomplete for coding channels. */

import { Paperclip, Send } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { agentsApi, filesApi, messagesApi } from "@/lib/api";
import { useChatStore } from "@/stores/chatStore";
import type { Agent } from "@/types";
import MentionAutocomplete from "./MentionAutocomplete";

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
  const [mentionQuery, setMentionQuery] = useState<string | null>(null);
  const [channelAgents, setChannelAgents] = useState<Agent[]>([]);
  const fileRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const addMessage = useChatStore((s) => s.addMessage);
  const channels = useChatStore((s) => s.channels);
  const currentChannel = channels.find((c) => c.id === channelId);
  const isCoding = currentChannel?.is_coding ?? false;

  // Load agents for coding channels
  useEffect(() => {
    if (!isCoding) return;
    agentsApi
      .listByChannel(channelId)
      .then(setChannelAgents)
      .catch(() => {});
  }, [channelId, isCoding]);

  // Detect @mention while typing
  const handleTextChange = useCallback(
    (value: string) => {
      setText(value);
      if (!isCoding) {
        setMentionQuery(null);
        return;
      }
      // Check if user is typing an @mention
      const cursorPos = textareaRef.current?.selectionStart ?? value.length;
      const textBeforeCursor = value.slice(0, cursorPos);
      const mentionMatch = textBeforeCursor.match(/@([\w-]*)$/);
      if (mentionMatch) {
        setMentionQuery(mentionMatch[1]);
      } else {
        setMentionQuery(null);
      }
    },
    [isCoding],
  );

  const handleMentionSelect = useCallback(
    (agentName: string) => {
      const cursorPos = textareaRef.current?.selectionStart ?? text.length;
      const textBeforeCursor = text.slice(0, cursorPos);
      const mentionMatch = textBeforeCursor.match(/@([\w-]*)$/);
      if (mentionMatch) {
        const beforeMention = textBeforeCursor.slice(
          0,
          mentionMatch.index! + 1,
        );
        const afterCursor = text.slice(cursorPos);
        const newText = `${beforeMention}${agentName} ${afterCursor}`;
        setText(newText);
        setMentionQuery(null);
        // Restore focus
        setTimeout(() => {
          const ta = textareaRef.current;
          if (ta) {
            const pos = beforeMention.length + agentName.length + 1;
            ta.focus();
            ta.setSelectionRange(pos, pos);
          }
        }, 0);
      }
    },
    [text],
  );

  // テキスト変更時にtextareaの高さを自動調整（最大160px）
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`;
  }, [text]);

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
      {/* Coding channel hint strip */}
      {isCoding && (
        <div className="mb-2 flex items-center gap-1.5 text-[11px] text-cyan-600 dark:text-cyan-400">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
          <span>@エージェント名 でエージェントへ指示を送信できます</span>
        </div>
      )}
      <div
        className={`relative flex items-end gap-2 bg-white/80 dark:bg-gray-800/60 border rounded-xl px-3 py-2.5 input-glow transition-all duration-200 ${
          isCoding
            ? "border-cyan-300/60 dark:border-cyan-700/40 focus-within:ring-2 focus-within:ring-cyan-500/20"
            : "border-gray-200/70 dark:border-gray-700/40 focus-within:ring-2 focus-within:ring-violet-500/20"
        }`}
      >
        {/* @mention autocomplete */}
        {mentionQuery !== null && (
          <MentionAutocomplete
            agents={channelAgents}
            query={mentionQuery}
            onSelect={handleMentionSelect}
            onClose={() => setMentionQuery(null)}
          />
        )}

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
          ref={textareaRef}
          value={text}
          onChange={(e) => handleTextChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            placeholder ??
            (isCoding
              ? "@エージェント名 で指示を送信..."
              : "メッセージを入力...")
          }
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 outline-none overflow-y-auto"
          style={{ maxHeight: "160px" }}
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
