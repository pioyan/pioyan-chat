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
    `flex items-center gap-2 px-3 py-1.5 rounded-lg cursor-pointer text-sm transition-all duration-150 ${
      currentChannelId === id
        ? "bg-gradient-to-r from-violet-600/80 to-fuchsia-600/60 text-white shadow-md"
        : "text-gray-400 hover:bg-white/8 hover:text-gray-100"
    }`;

  const displayName = currentUser
    ? currentUser.username || currentUser.email
    : "…";
  const avatarLetter = displayName[0]?.toUpperCase() ?? "?";

  return (
    <>
      <aside className="w-60 flex flex-col h-full bg-gray-950/95 backdrop-blur-sm border-r border-violet-500/10">
        {/* Workspace header */}
        <div className="px-4 py-3.5 border-b border-white/5">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-md shrink-0">
              <MessageCircle size={14} className="text-white" />
            </div>
            <h1 className="font-bold text-white text-base tracking-tight">
              pioyan-chat
            </h1>
          </div>
        </div>

        {/* Search button */}
        <button
          onClick={() => setSearchOpen(true)}
          className="flex items-center gap-2 mx-3 my-2 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/8 hover:border-white/15 rounded-lg text-gray-400 hover:text-gray-200 text-sm transition-all duration-150"
        >
          <Search size={14} />
          <span>検索</span>
        </button>

        {/* Channel list */}
        <div className="flex-1 overflow-y-auto">
          <div className="px-3 pt-3 pb-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 uppercase tracking-widest select-none">
                チャンネル
              </span>
              <button
                className="text-gray-500 hover:text-white transition-colors"
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
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-widest">
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
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-widest">
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
        <div className="border-t border-white/8 px-3 py-2.5 flex items-center gap-2 bg-white/3">
          {currentUser?.avatar_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={currentUser.avatar_url}
              alt="アバター"
              className="w-8 h-8 rounded-full object-cover shrink-0"
            />
          ) : (
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-sm font-bold shrink-0 shadow-md">
              {avatarLetter}
            </div>
          )}
          <span className="flex-1 text-sm text-gray-300 truncate">
            {displayName}
          </span>
          <button
            onClick={onProfileClick}
            className="text-gray-400 hover:text-violet-300 shrink-0 transition-colors"
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
