"use client";
/** Left sidebar: channel list + DM list. */

import {
  Hash,
  Lock,
  MessageCircle,
  Plus,
  Search,
  Settings,
} from "lucide-react";
import { useState } from "react";
import type { Channel, User } from "@/types";
import { useChatStore } from "@/stores/chatStore";
import CreateChannelModal from "./CreateChannelModal";

interface Props {
  channels: Channel[];
  dms: Channel[];
  currentChannelId: string | null;
  currentUser: User | null;
  onChannelCreated: (channel: Channel) => void;
  onProfileClick: () => void;
}

export default function Sidebar({
  channels,
  dms,
  currentChannelId,
  currentUser,
  onChannelCreated,
  onProfileClick,
}: Props) {
  const { setCurrentChannel, setSearchOpen } = useChatStore();
  const [createChannelOpen, setCreateChannelOpen] = useState(false);

  const publicChannels = channels.filter((c) => !c.is_private && !c.is_direct);
  const privateChannels = channels.filter((c) => c.is_private && !c.is_direct);

  const itemClass = (id: string) =>
    `flex items-center gap-2 px-3 py-1 rounded cursor-pointer text-sm transition-colors ${
      currentChannelId === id
        ? "bg-violet-600 text-white"
        : "text-zinc-300 hover:bg-zinc-700 hover:text-white"
    }`;

  const displayName = currentUser
    ? currentUser.username || currentUser.email
    : "…";
  const avatarLetter = displayName[0]?.toUpperCase() ?? "?";

  return (
    <>
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

        {/* Channel list */}
        <div className="flex-1 overflow-y-auto">
          <div className="px-3 pt-3 pb-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">
                チャンネル
              </span>
              <button
                className="text-zinc-400 hover:text-white"
                aria-label="チャンネル追加"
                onClick={() => setCreateChannelOpen(true)}
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

        {/* User info footer */}
        <div className="border-t border-zinc-700 px-3 py-2 flex items-center gap-2">
          {currentUser?.avatar_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={currentUser.avatar_url}
              alt="アバター"
              className="w-8 h-8 rounded-full object-cover shrink-0"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-violet-600 flex items-center justify-center text-white text-sm font-bold shrink-0">
              {avatarLetter}
            </div>
          )}
          <span className="flex-1 text-sm text-zinc-300 truncate">
            {displayName}
          </span>
          <button
            onClick={onProfileClick}
            className="text-zinc-400 hover:text-white shrink-0"
            aria-label="プロフィール設定"
          >
            <Settings size={14} />
          </button>
        </div>
      </aside>

      {createChannelOpen && (
        <CreateChannelModal
          onClose={() => setCreateChannelOpen(false)}
          onCreated={(ch) => {
            onChannelCreated(ch);
            setCreateChannelOpen(false);
          }}
        />
      )}
    </>
  );
}
