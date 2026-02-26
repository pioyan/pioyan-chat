"use client";
/** Search modal for message search. */

import { Search, X } from "lucide-react";
import { useEffect, useState } from "react";
import { messagesApi } from "@/lib/api";
import { useChatStore } from "@/stores/chatStore";
import type { Message } from "@/types";

export default function SearchModal() {
  const { searchOpen, setSearchOpen, setCurrentChannel } = useChatStore();
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
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 pt-20">
      <div className="w-full max-w-lg bg-white dark:bg-zinc-900 rounded-xl shadow-2xl overflow-hidden">
        {/* Search input */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-zinc-200 dark:border-zinc-700">
          <Search size={16} className="text-zinc-400" />
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="メッセージを検索..."
            className="flex-1 bg-transparent text-sm text-zinc-900 dark:text-zinc-100 placeholder-zinc-400 outline-none"
          />
          <button
            onClick={() => setSearchOpen(false)}
            className="text-zinc-400 hover:text-zinc-900"
            aria-label="閉じる"
          >
            <X size={16} />
          </button>
        </div>

        {/* Results */}
        <div className="max-h-80 overflow-y-auto">
          {loading && (
            <p className="text-center text-sm text-zinc-400 py-4">検索中...</p>
          )}
          {!loading && results.length === 0 && query && (
            <p className="text-center text-sm text-zinc-400 py-4">結果なし</p>
          )}
          {results.map((msg) => (
            <button
              key={msg.id}
              onClick={() => handleSelect(msg)}
              className="w-full text-left px-4 py-3 hover:bg-zinc-50 dark:hover:bg-zinc-800 border-b border-zinc-100 dark:border-zinc-800"
            >
              <p className="text-xs text-zinc-400 mb-1">#{msg.channel_id}</p>
              <p className="text-sm text-zinc-900 dark:text-zinc-100 line-clamp-2">
                {msg.content}
              </p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
