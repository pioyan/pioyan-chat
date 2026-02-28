"use client";
/** Left sidebar: channel list + DM list. */

import { Code2, Hash, Lock, MessageCircle, Plus, Settings } from "lucide-react";
import { useState } from "react";
import type { Channel, User } from "@/types";
import { useChatStore } from "@/stores/chatStore";
import CreateChannelModal from "./CreateChannelModal";
import CreateCodingChannelModal from "./CreateCodingChannelModal";
import type { NavSection } from "./AppNavBar";

interface Props {
  channels: Channel[];
  dms: Channel[];
  currentChannelId: string | null;
  currentUser: User | null;
  onChannelCreated: (channel: Channel) => void;
  onProfileClick: () => void;
  /** AppNavBar から渡されるアクティブセクション */
  activeSection: NavSection;
}

export default function Sidebar({
  channels,
  dms,
  currentChannelId,
  currentUser,
  onChannelCreated,
  onProfileClick,
  activeSection,
}: Props) {
  const { setCurrentChannel } = useChatStore();
  const [createChannelOpen, setCreateChannelOpen] = useState(false);
  const [createCodingOpen, setCreateCodingOpen] = useState(false);

  const publicChannels = channels.filter(
    (c) => !c.is_private && !c.is_direct && !c.is_coding,
  );
  const privateChannels = channels.filter(
    (c) => c.is_private && !c.is_direct && !c.is_coding,
  );
  const codingChannels = channels.filter((c) => c.is_coding);

  const itemClass = (id: string, isCoding = false) =>
    `flex items-center gap-2 px-3 py-1.5 rounded-lg cursor-pointer text-sm transition-all duration-150 ${
      currentChannelId === id
        ? isCoding
          ? "bg-gradient-to-r from-cyan-600/80 to-violet-600/60 text-white shadow-md"
          : "bg-gradient-to-r from-violet-600/80 to-fuchsia-600/60 text-white shadow-md"
        : "text-gray-400 hover:bg-white/8 hover:text-gray-100"
    }`;

  const displayName = currentUser
    ? currentUser.username || currentUser.email
    : "…";
  const avatarLetter = displayName[0]?.toUpperCase() ?? "?";

  return (
    <>
      <aside className="w-60 flex flex-col h-full bg-gray-950/95 backdrop-blur-sm border-r border-violet-500/10">
        {/* セクションヘッダー */}
        <div className="px-4 py-3 border-b border-white/5">
          <h2 className="font-semibold text-sm text-gray-200 tracking-tight">
            {activeSection === "channels"
              ? "チャンネル"
              : activeSection === "dms"
                ? "ダイレクトメッセージ"
                : "ボット管理"}
          </h2>
        </div>

        {/* リスト */}
        <div className="flex-1 overflow-y-auto">
          {activeSection === "channels" ? (
            <>
              {/* パブリックチャンネル */}
              <div className="px-3 pt-3 pb-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-widest select-none">
                    パブリック
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

              {/* プライベートチャンネル */}
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
              {/* コーディングチャンネル */}
              <div className="px-3 pt-3 pb-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-widest select-none">
                    コーディング
                  </span>
                  <button
                    className="text-gray-500 hover:text-white transition-colors"
                    aria-label="コーディングチャンネル追加"
                    onClick={() => setCreateCodingOpen(true)}
                  >
                    <Plus size={14} />
                  </button>
                </div>
              </div>
              {codingChannels.map((ch) => (
                <div
                  key={ch.id}
                  className={itemClass(ch.id, true)}
                  onClick={() => setCurrentChannel(ch.id)}
                >
                  <Code2
                    size={14}
                    className={
                      currentChannelId === ch.id
                        ? "text-cyan-200"
                        : "text-cyan-500"
                    }
                  />
                  <span className="flex-1 truncate">{ch.name}</span>
                  {ch.repo_name && currentChannelId !== ch.id && (
                    <span className="text-[10px] text-gray-500 font-mono truncate max-w-[5rem] shrink-0">
                      {ch.repo_name}
                    </span>
                  )}
                </div>
              ))}
            </>
          ) : (
            <>
              {/* DM リスト */}
              {dms.length === 0 ? (
                <div className="px-4 py-6 text-center">
                  <MessageCircle
                    size={32}
                    className="mx-auto text-gray-600 mb-2"
                  />
                  <p className="text-xs text-gray-500">まだ DM はありません</p>
                </div>
              ) : (
                dms.map((dm) => (
                  <div
                    key={dm.id}
                    className={itemClass(dm.id)}
                    onClick={() => setCurrentChannel(dm.id)}
                  >
                    <div className="w-5 h-5 rounded-full bg-gradient-to-br from-violet-400 to-fuchsia-400 flex items-center justify-center text-white text-xs font-bold shrink-0">
                      {dm.name?.[0]?.toUpperCase() ?? "?"}
                    </div>
                    <span className="truncate">{dm.name}</span>
                  </div>
                ))
              )}
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

      {createCodingOpen && (
        <CreateCodingChannelModal
          onClose={() => setCreateCodingOpen(false)}
          onCreated={(ch) => {
            onChannelCreated(ch);
            setCreateCodingOpen(false);
          }}
        />
      )}
    </>
  );
}
