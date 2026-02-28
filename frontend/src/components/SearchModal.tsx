"use client";
/** Search modal for message search. */

import { Search, X } from "lucide-react";
import { useEffect, useState } from "react";
import { messagesApi } from "@/lib/api";
import { useChatStore } from "@/stores/chatStore";
import type { Message } from "@/types";

export default function SearchModal() {
  const { searchOpen, setSearchOpen, setCurrentChannel, channels } =
    useChatStore();
  const channelMap = new Map(channels.map((c) => [c.id, c.name]));
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await messagesApi.search(query);
        setResults(res);
      } finally {
        setLoading(false);
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  if (!searchOpen) return null;

  const handleSelect = (msg: Message) => {
    setCurrentChannel(msg.channel_id);
    setSearchOpen(false);
    setQuery("");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 backdrop-blur-sm pt-20">
      <div className="w-full max-w-lg bg-white/90 dark:bg-gray-900/90 backdrop-blur-xl rounded-2xl border border-white/50 dark:border-violet-500/20 shadow-2xl glow-surface overflow-hidden">
        {/* Search input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200/50 dark:border-gray-700/30">
          <Search size={16} className="text-violet-400" />
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="メッセージを検索..."
            className="flex-1 bg-transparent text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 outline-none"
          />
          <button
            onClick={() => setSearchOpen(false)}
            className="text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
            aria-label="閉じる"
          >
            <X size={16} />
          </button>
        </div>

        {/* Results */}
        <div className="max-h-80 overflow-y-auto">
          {loading && (
            <p className="text-center text-sm text-gray-400 py-4">検索中...</p>
          )}
          {!loading && results.length === 0 && query && (
            <p className="text-center text-sm text-gray-400 py-4">結果なし</p>
          )}
          {results.map((msg) => (
            <button
              key={msg.id}
              onClick={() => handleSelect(msg)}
              className="w-full text-left px-4 py-3 hover:bg-violet-50/40 dark:hover:bg-violet-900/20 border-b border-gray-100/50 dark:border-gray-800/50 transition-colors"
            >
              <p className="text-xs text-violet-500 dark:text-violet-400 mb-1">
                #{channelMap.get(msg.channel_id) ?? msg.channel_id}
              </p>
              <p className="text-sm text-gray-900 dark:text-gray-100 line-clamp-2">
                {msg.content}
              </p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
