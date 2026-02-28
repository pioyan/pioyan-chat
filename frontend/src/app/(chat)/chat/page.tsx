"use client";
/** Main chat page — Slack-style 3-column layout. */

import { Bot, Code2, ExternalLink, Hash, MessageCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authApi, channelsApi, dmApi, messagesApi } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { useSocket } from "@/hooks/useSocket";
import { useChatStore } from "@/stores/chatStore";
import type { Channel } from "@/types";
import AgentPanel from "@/components/AgentPanel";
import BotManagementPanel from "@/components/BotManagementPanel";
import MessageInput from "@/components/MessageInput";
import MessageList from "@/components/MessageList";
import ProfileModal from "@/components/ProfileModal";
import SearchModal from "@/components/SearchModal";
import Sidebar from "@/components/Sidebar";
import ThreadPanel from "@/components/ThreadPanel";
import AppNavBar from "@/components/AppNavBar";
import type { NavSection } from "@/components/AppNavBar";

export default function ChatPage() {
  const router = useRouter();
  const {
    channels,
    currentChannelId,
    currentUser,
    messages,
    threadMessageId,
    agentPanelOpen,
    setChannels,
    addChannel,
    setCurrentUser,
    setMessages,
    setCurrentChannel,
    setThreadMessageId,
    setAgentPanelOpen,
  } = useChatStore();
  const [dms, setDms] = useState(
    useChatStore.getState().channels.filter((c) => c.is_direct),
  );
  const [profileOpen, setProfileOpen] = useState(false);
  const [navSection, setNavSection] = useState<NavSection>("channels");

  // Socket.IO 接続
  useSocket();

  // 初期データロード
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    const load = async () => {
      try {
        const [user, channelList, dmList] = await Promise.all([
          authApi.me(),
          channelsApi.list(),
          dmApi.list(),
        ]);
        setCurrentUser(user);
        setChannels([...channelList, ...dmList]);
        setDms(dmList);
        // 最初のチャンネルを選択
        if (channelList.length > 0 && !currentChannelId) {
          setCurrentChannel(channelList[0].id);
        }
      } catch {
        router.push("/login");
      }
    };
    void load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // チャンネル切り替えでメッセージを読み込む
  useEffect(() => {
    if (!currentChannelId) return;
    messagesApi.list(currentChannelId).then((msgs) => {
      setMessages(currentChannelId, msgs);
    });
  }, [currentChannelId, setMessages]);

  const handleChannelCreated = (channel: Channel) => {
    addChannel(channel);
    setCurrentChannel(channel.id);
  };

  const currentChannel = channels.find((c) => c.id === currentChannelId);
  const currentMessages = currentChannelId
    ? (messages[currentChannelId] ?? [])
    : [];

  return (
    <div className="flex h-screen bg-gradient-to-br from-white via-violet-50/20 to-white dark:from-gray-950 dark:via-violet-950/10 dark:to-gray-950 overflow-hidden">
      {/* App nav bar (icon strip) */}
      <AppNavBar
        activeSection={navSection}
        onSectionChange={(section) => {
          setNavSection(section);
          // DM セクションに切り替えたとき、1番目の DM を自動選択
          if (
            section === "dms" &&
            dms.length > 0 &&
            !dms.find((d) => d.id === currentChannelId)
          ) {
            setCurrentChannel(dms[0].id);
          }
        }}
        onSearchClick={() => useChatStore.getState().setSearchOpen(true)}
        onSettingsClick={() => setProfileOpen(true)}
      />

      {/* Left sidebar */}
      <Sidebar
        channels={channels.filter((c) => !c.is_direct)}
        dms={dms}
        currentChannelId={currentChannelId}
        currentUser={currentUser}
        onChannelCreated={handleChannelCreated}
        onProfileClick={() => setProfileOpen(true)}
        activeSection={navSection}
      />

      {/* Main content */}
      {navSection === "bots" ? (
        <BotManagementPanel />
      ) : (
        <>
          <div className="flex-1 flex flex-col min-w-0">
            {/* Channel header */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-200/50 dark:border-gray-700/30 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
              {currentChannel?.is_coding ? (
                <Code2 size={16} className="text-cyan-400 shrink-0" />
              ) : currentChannel?.is_direct ? (
                <MessageCircle size={16} className="text-fuchsia-400 shrink-0" />
              ) : (
                <Hash size={16} className="text-violet-400 shrink-0" />
              )}
              <h2 className="font-semibold text-sm text-gray-900 dark:text-gray-100 tracking-tight">
                {currentChannel?.name ?? "チャンネルを選択"}
              </h2>
              {currentChannel?.description && (
                <span className="text-xs text-gray-400 ml-2 truncate">
                  {currentChannel.description}
                </span>
              )}
              {currentChannel?.is_coding && (
                <>
                  {currentChannel.repo_owner && currentChannel.repo_name && (
                    <a
                      href={`https://github.com/${currentChannel.repo_owner}/${currentChannel.repo_name}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-cyan-50 dark:bg-cyan-900/20 border border-cyan-200/60 dark:border-cyan-700/30 text-cyan-600 dark:text-cyan-400 hover:bg-cyan-100 dark:hover:bg-cyan-900/40 transition-colors font-mono"
                    >
                      <ExternalLink size={9} />
                      {currentChannel.repo_owner}/{currentChannel.repo_name}
                    </a>
                  )}
                  <div className="flex-1" />
                  <button
                    onClick={() => setAgentPanelOpen(!agentPanelOpen)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 ${
                      agentPanelOpen
                        ? "bg-gradient-to-r from-cyan-500/20 to-violet-500/20 dark:from-cyan-900/40 dark:to-violet-900/40 text-cyan-700 dark:text-cyan-300 border border-cyan-300/40 dark:border-cyan-700/40 shadow-sm"
                        : "text-gray-400 hover:text-cyan-600 dark:hover:text-cyan-400 hover:bg-cyan-50 dark:hover:bg-cyan-900/20 border border-transparent hover:border-cyan-200/50 dark:hover:border-cyan-700/30"
                    }`}
                    title="エージェント & タスク"
                  >
                    <Bot size={13} />
                    <span>エージェント</span>
                  </button>
                </>
              )}
            </div>

            {/* Message area */}
            {currentChannelId ? (
              <>
                <MessageList
                  messages={currentMessages}
                  onThreadClick={(id) => setThreadMessageId(id)}
                />
                <MessageInput channelId={currentChannelId} />
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-400">
                <p>チャンネルを選択してください</p>
              </div>
            )}
          </div>

          {/* Thread panel */}
          {threadMessageId && <ThreadPanel />}

          {/* Agent panel (coding channels) */}
          {agentPanelOpen && currentChannelId && currentChannel?.is_coding && (
            <AgentPanel
              channelId={currentChannelId}
              onClose={() => setAgentPanelOpen(false)}
            />
          )}
        </>
      )}

      {/* Search modal */}
      <SearchModal />

      {/* Profile modal */}
      {profileOpen && currentUser && (
        <ProfileModal
          user={currentUser}
          onClose={() => setProfileOpen(false)}
          onUpdated={(updated) => {
            setCurrentUser(updated);
            setProfileOpen(false);
          }}
        />
      )}
    </div>
  );
}
