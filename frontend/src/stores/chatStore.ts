"use client";
/** Zustand store for pioyan-chat. */

import { create } from "zustand";
import type { Channel, Message, User } from "@/types";

interface ChatState {
  // Data
  channels: Channel[];
  currentChannelId: string | null;
  messages: Record<string, Message[]>; // channelId → messages
  currentUser: User | null;

  // UI
  sidebarOpen: boolean;
  threadMessageId: string | null;
  searchOpen: boolean;

  // Actions
  setChannels: (channels: Channel[]) => void;
  addChannel: (channel: Channel) => void;
  setCurrentChannel: (id: string | null) => void;
  setMessages: (channelId: string, messages: Message[]) => void;
  addMessage: (message: Message) => void;
  setCurrentUser: (user: User | null) => void;
  toggleSidebar: () => void;
  setThreadMessageId: (id: string | null) => void;
  setSearchOpen: (open: boolean) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  channels: [],
  currentChannelId: null,
  messages: {},
  currentUser: null,
  sidebarOpen: true,
  threadMessageId: null,
  searchOpen: false,

  setChannels: (channels) => set({ channels }),
  addChannel: (channel) =>
    set((state) => ({
      channels: [...state.channels.filter((c) => c.id !== channel.id), channel],
    })),
  setCurrentChannel: (id) =>
    set({ currentChannelId: id, threadMessageId: null }),
  setMessages: (channelId, messages) =>
    set((state) => ({
      messages: { ...state.messages, [channelId]: messages },
    })),
  addMessage: (message) =>
    set((state) => {
      const existing = state.messages[message.channel_id] ?? [];
      return {
        messages: {
          ...state.messages,
          [message.channel_id]: [...existing, message],
        },
      };
    }),
  setCurrentUser: (user) => set({ currentUser: user }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setThreadMessageId: (id) => set({ threadMessageId: id }),
  setSearchOpen: (open) => set({ searchOpen: open }),
}));
