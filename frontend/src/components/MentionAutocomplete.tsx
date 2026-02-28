"use client";
/** @mention autocomplete dropdown for agent names — keyboard nav support. */

import { Bot } from "lucide-react";
import { useEffect, useState } from "react";
import type { Agent } from "@/types";

interface Props {
  agents: Agent[];
  query: string;
  onSelect: (agentName: string) => void;
  onClose?: () => void;
}

export default function MentionAutocomplete({
  agents,
  query,
  onSelect,
  onClose,
}: Props) {
  const [activeIdx, setActiveIdx] = useState(0);
  // Derived state: reset active index when query changes (render-phase update)
  const [prevQuery, setPrevQuery] = useState(query);
  if (prevQuery !== query) {
    setPrevQuery(query);
    setActiveIdx(0);
  }

  const filtered = agents.filter((a) =>
    a.name.toLowerCase().startsWith(query.toLowerCase()),
  );

  // Keyboard navigation
  useEffect(() => {
    if (filtered.length === 0) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        e.stopPropagation();
        setActiveIdx((i) => (i + 1) % filtered.length);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        e.stopPropagation();
        setActiveIdx((i) => (i - 1 + filtered.length) % filtered.length);
      } else if (e.key === "Enter") {
        e.preventDefault();
        e.stopPropagation();
        onSelect(filtered[activeIdx].name);
      } else if (e.key === "Escape") {
        e.preventDefault();
        e.stopPropagation();
        onClose?.();
      }
    };

    window.addEventListener("keydown", handleKeyDown, { capture: true });
    return () =>
      window.removeEventListener("keydown", handleKeyDown, { capture: true });
  }, [filtered, activeIdx, onSelect, onClose]);

  if (filtered.length === 0) return null;

  return (
    <div className="absolute bottom-full left-0 right-0 mb-2 overflow-hidden bg-white/98 dark:bg-gray-900/98 backdrop-blur-xl border border-violet-200/70 dark:border-violet-500/30 rounded-xl shadow-2xl z-10">
      {/* Header */}
      <div className="flex items-center gap-1.5 px-3 py-1.5 border-b border-gray-100/60 dark:border-gray-800/60 bg-violet-50/40 dark:bg-violet-950/20">
        <span className="text-[10px] font-semibold text-violet-500 dark:text-violet-400 uppercase tracking-widest">
          エージェントへメンション
        </span>
        <span className="ml-auto text-[10px] text-gray-400 hidden sm:block">
          ↑↓ で移動 · Enter で選択 · Esc で閉じる
        </span>
      </div>

      {/* Items */}
      <div className="max-h-44 overflow-y-auto py-1">
        {filtered.map((agent, idx) => (
          <button
            key={agent.id}
            type="button"
            onMouseDown={(e) => {
              e.preventDefault();
              onSelect(agent.name);
            }}
            onMouseEnter={() => setActiveIdx(idx)}
            className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm text-left transition-colors duration-100 ${
              idx === activeIdx
                ? "bg-violet-50 dark:bg-violet-900/40"
                : "hover:bg-gray-50/80 dark:hover:bg-gray-800/40"
            }`}
          >
            {/* Avatar */}
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 transition-all duration-150 ${
                idx === activeIdx
                  ? "bg-gradient-to-br from-violet-500 to-fuchsia-500 shadow-md shadow-violet-500/30"
                  : "bg-gradient-to-br from-violet-400/60 to-fuchsia-400/60"
              }`}
            >
              <Bot size={10} className="text-white" />
            </div>

            {/* Name + description */}
            <div className="flex-1 min-w-0 flex items-baseline gap-1.5">
              <span
                className={`font-semibold ${
                  idx === activeIdx
                    ? "text-violet-700 dark:text-violet-300"
                    : "text-gray-700 dark:text-gray-200"
                }`}
              >
                @{agent.name}
              </span>
              {agent.description && (
                <span className="text-xs text-gray-400 truncate">
                  {agent.description}
                </span>
              )}
            </div>

            {/* Active hint */}
            {idx === activeIdx && (
              <kbd className="shrink-0 text-[9px] px-1.5 py-0.5 rounded bg-violet-100 dark:bg-violet-900/50 text-violet-500 font-mono">
                Enter
              </kbd>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
