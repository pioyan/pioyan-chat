"use client";
/** Left sidebar: channel list + DM list. */

import { Hash, Lock, MessageCircle, Plus, Search } from "lucide-react";
import type { Channel } from "@/types";
import { useChatStore } from "@/stores/chatStore";

interface Props {
  channels: Channel[];
  dms: Channel[];
  currentChannelId: string | null;
}

export default function Sidebar({ channels, dms, currentChannelId }: Props) {
  const { setCurrentChannel, setSearchOpen } = useChatStore();
  const publicChannels = channels.filter((c) => !c.is_private && !c.is_direct);
  const privateChannels = channels.filter((c) => c.is_private && !c.is_direct);

  const itemClass = (id: string) =>
    `flex items-center gap-2 px-3 py-1 rounded cursor-pointer text-sm transition-colors ${
      currentChannelId === id
        ? "bg-violet-600 text-white"
        : "text-zinc-300 hover:bg-zinc-700 hover:text-white"
    }`;

  return (
    <aside className="w-60 bg-zinc-900 flex flex-col h-full">
      {/* Workspace header */}
      <div className="px-4 py-3 border-b border-zinc-700">
        <h1 className="font-bold text-white text-lg">pioyan-chat</h1>
      </div>

      {/* Search button */}
      <button
        onClick={() => setSearchOpen(true)}
        className="flex items-center gap-2 mx-3 my-2 px-3 py-1.5 bg-zinc-700 hover:bg-zinc-600 rounded text-zinc-300 text-sm"
      >
        <Search size={14} />
        <span>検索</span>
      </button>

      {/* Public channels */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-3 pt-3 pb-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">
              チャンネル
            </span>
            <button
              className="text-zinc-400 hover:text-white"
              aria-label="チャンネル追加"
            >
              <Plus size={14} />
            </button>
          </div>
        </div>
        {publicChannels.map((ch) => (
          <div
            key={ch.id}
            className={itemClass(ch.id)}
            onClick={() => setCurrentChannel(ch.id)}
          >
            <Hash size={14} />
            <span className="truncate">{ch.name}</span>
          </div>
        ))}

        {/* Private channels */}
        {privateChannels.length > 0 && (
          <>
            <div className="px-3 pt-3 pb-1">
              <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">
                プライベート
              </span>
            </div>
            {privateChannels.map((ch) => (
              <div
                key={ch.id}
                className={itemClass(ch.id)}
                onClick={() => setCurrentChannel(ch.id)}
              >
                <Lock size={14} />
                <span className="truncate">{ch.name}</span>
              </div>
            ))}
          </>
        )}

        {/* DMs */}
        {dms.length > 0 && (
          <>
            <div className="px-3 pt-3 pb-1">
              <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">
                ダイレクトメッセージ
              </span>
            </div>
            {dms.map((dm) => (
              <div
                key={dm.id}
                className={itemClass(dm.id)}
                onClick={() => setCurrentChannel(dm.id)}
              >
                <MessageCircle size={14} />
                <span className="truncate">{dm.name}</span>
              </div>
            ))}
          </>
        )}
      </div>
    </aside>
  );
}
