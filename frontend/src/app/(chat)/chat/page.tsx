"use client";
/** Main chat page — Slack-style 3-column layout. */

import { Hash } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authApi, channelsApi, dmApi, messagesApi } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { useSocket } from "@/hooks/useSocket";
import { useChatStore } from "@/stores/chatStore";
import type { Channel } from "@/types";
import MessageInput from "@/components/MessageInput";
import MessageList from "@/components/MessageList";
import ProfileModal from "@/components/ProfileModal";
import SearchModal from "@/components/SearchModal";
import Sidebar from "@/components/Sidebar";
import ThreadPanel from "@/components/ThreadPanel";

export default function ChatPage() {
  const router = useRouter();
  const {
    channels,
    currentChannelId,
    currentUser,
    messages,
    threadMessageId,
    setChannels,
    addChannel,
    setCurrentUser,
    setMessages,
    setCurrentChannel,
    setThreadMessageId,
  } = useChatStore();
  const [dms, setDms] = useState(
    useChatStore.getState().channels.filter((c) => c.is_direct),
  );
  const [profileOpen, setProfileOpen] = useState(false);

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
      {/* Left sidebar */}
      <Sidebar
        channels={channels.filter((c) => !c.is_direct)}
        dms={dms}
        currentChannelId={currentChannelId}
        currentUser={currentUser}
        onChannelCreated={handleChannelCreated}
        onProfileClick={() => setProfileOpen(true)}
      />

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Channel header */}
        <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-200/50 dark:border-gray-700/30 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
          <Hash size={16} className="text-violet-400" />
          <h2 className="font-semibold text-sm text-gray-900 dark:text-gray-100 tracking-tight">
            {currentChannel?.name ?? "チャンネルを選択"}
          </h2>
          {currentChannel?.description && (
            <span className="text-xs text-gray-400 ml-2">
              {currentChannel.description}
            </span>
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
