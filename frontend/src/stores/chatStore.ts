"use client";
/** Zustand store for pioyan-chat. */

import { create } from "zustand";
import type { Agent, Channel, CodingTask, Message, User } from "@/types";

interface ChatState {
  // Data
  channels: Channel[];
  currentChannelId: string | null;
  messages: Record<string, Message[]>; // channelId → messages
  currentUser: User | null;

  // Coding channel data
  channelAgents: Record<string, Agent[]>; // channelId → agents
  channelTasks: Record<string, CodingTask[]>; // channelId → tasks
  agentPanelOpen: boolean;

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
  incrementReplyCount: (channelId: string, messageId: string) => void;
  setCurrentUser: (user: User | null) => void;
  toggleSidebar: () => void;
  setThreadMessageId: (id: string | null) => void;
  setSearchOpen: (open: boolean) => void;

  // Coding actions
  setChannelAgents: (channelId: string, agents: Agent[]) => void;
  setChannelTasks: (channelId: string, tasks: CodingTask[]) => void;
  addCodingTask: (task: CodingTask) => void;
  updateCodingTask: (task: CodingTask) => void;
  setAgentPanelOpen: (open: boolean) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  channels: [],
  currentChannelId: null,
  messages: {},
  currentUser: null,
  channelAgents: {},
  channelTasks: {},
  agentPanelOpen: false,
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
  incrementReplyCount: (channelId, messageId) =>
    set((state) => {
      const existing = state.messages[channelId] ?? [];
      return {
        messages: {
          ...state.messages,
          [channelId]: existing.map((m) =>
            m.id === messageId ? { ...m, reply_count: m.reply_count + 1 } : m,
          ),
        },
      };
    }),
  setCurrentUser: (user) => set({ currentUser: user }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setThreadMessageId: (id) => set({ threadMessageId: id }),
  setSearchOpen: (open) => set({ searchOpen: open }),

  // Coding actions
  setChannelAgents: (channelId, agents) =>
    set((state) => ({
      channelAgents: { ...state.channelAgents, [channelId]: agents },
    })),
  setChannelTasks: (channelId, tasks) =>
    set((state) => ({
      channelTasks: { ...state.channelTasks, [channelId]: tasks },
    })),
  addCodingTask: (task) =>
    set((state) => {
      const existing = state.channelTasks[task.channel_id] ?? [];
      return {
        channelTasks: {
          ...state.channelTasks,
          [task.channel_id]: [task, ...existing],
        },
      };
    }),
  updateCodingTask: (task) =>
    set((state) => {
      const existing = state.channelTasks[task.channel_id] ?? [];
      return {
        channelTasks: {
          ...state.channelTasks,
          [task.channel_id]: existing.map((t) => (t.id === task.id ? task : t)),
        },
      };
    }),
  setAgentPanelOpen: (open) => set({ agentPanelOpen: open }),
}));
