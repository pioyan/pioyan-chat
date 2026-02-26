/**
 * Tests for Zustand chatStore
 */
import { describe, it, expect, beforeEach } from "vitest";

describe("chatStore", () => {
  beforeEach(async () => {
    // ストアをリセット
    const { useChatStore } = await import("@/stores/chatStore");
    useChatStore.setState({
      channels: [],
      currentChannelId: null,
      messages: {},
      currentUser: null,
      sidebarOpen: true,
      threadMessageId: null,
    });
  });

  it("sets current channel", async () => {
    const { useChatStore } = await import("@/stores/chatStore");
    const { setCurrentChannel } = useChatStore.getState();
    setCurrentChannel("channel-123");
    expect(useChatStore.getState().currentChannelId).toBe("channel-123");
  });

  it("adds a message to channel", async () => {
    const { useChatStore } = await import("@/stores/chatStore");
    const { addMessage } = useChatStore.getState();
    const msg = {
      id: "msg-1",
      channel_id: "ch-1",
      sender_id: "user-1",
      content: "Hello!",
      file_url: null,
      thread_id: null,
      reply_count: 0,
      created_at: new Date().toISOString(),
      updated_at: null,
    };
    addMessage(msg);
    expect(useChatStore.getState().messages["ch-1"]).toHaveLength(1);
    expect(useChatStore.getState().messages["ch-1"][0].content).toBe("Hello!");
  });

  it("sets channels list", async () => {
    const { useChatStore } = await import("@/stores/chatStore");
    const { setChannels } = useChatStore.getState();
    const channels = [
      {
        id: "ch-1",
        name: "general",
        description: null,
        is_private: false,
        is_direct: false,
        members: [],
        created_by: "user-1",
        created_at: new Date().toISOString(),
      },
    ];
    setChannels(channels);
    expect(useChatStore.getState().channels).toHaveLength(1);
    expect(useChatStore.getState().channels[0].name).toBe("general");
  });

  it("toggles sidebar", async () => {
    const { useChatStore } = await import("@/stores/chatStore");
    const initial = useChatStore.getState().sidebarOpen;
    useChatStore.getState().toggleSidebar();
    expect(useChatStore.getState().sidebarOpen).toBe(!initial);
  });

  it("sets thread message", async () => {
    const { useChatStore } = await import("@/stores/chatStore");
    useChatStore.getState().setThreadMessageId("msg-42");
    expect(useChatStore.getState().threadMessageId).toBe("msg-42");
  });
});
