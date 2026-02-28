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
      channelAgents: {},
      channelTasks: {},
      agentPanelOpen: false,
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
      sender_username: "testuser",
      sender_avatar_url: null,
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
        is_coding: false,
        members: [],
        repo_url: null,
        repo_owner: null,
        repo_name: null,
        default_branch: "main",
        assigned_agents: [],
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

  it("increments reply count for a message", async () => {
    const { useChatStore } = await import("@/stores/chatStore");
    const { setMessages, incrementReplyCount } = useChatStore.getState();
    setMessages("ch-1", [
      {
        id: "msg-1",
        channel_id: "ch-1",
        sender_id: "user-1",
        sender_username: "testuser",
        sender_avatar_url: null,
        content: "Hello!",
        file_url: null,
        thread_id: null,
        reply_count: 0,
        created_at: new Date().toISOString(),
        updated_at: null,
      },
    ]);
    incrementReplyCount("ch-1", "msg-1");
    const msgs = useChatStore.getState().messages["ch-1"];
    expect(msgs[0].reply_count).toBe(1);
  });

  // ── Coding channel store tests ──

  it("sets channel agents", async () => {
    const { useChatStore } = await import("@/stores/chatStore");
    const agents = [
      {
        id: "a1",
        name: "code-bot",
        description: null,
        system_prompt: null,
        source: "manual" as const,
        repo_agent_path: null,
        status: "registered" as const,
        owner_id: "u1",
        created_at: new Date().toISOString(),
      },
    ];
    useChatStore.getState().setChannelAgents("ch-1", agents);
    expect(useChatStore.getState().channelAgents["ch-1"]).toHaveLength(1);
  });

  it("adds a coding task", async () => {
    const { useChatStore } = await import("@/stores/chatStore");
    const task = {
      id: "t1",
      channel_id: "ch-1",
      agent_id: "a1",
      user_id: "u1",
      instruction: "Fix bug",
      status: "pending" as const,
      result_summary: null,
      commit_sha: null,
      pr_url: null,
      branch_name: null,
      created_at: new Date().toISOString(),
      completed_at: null,
    };
    useChatStore.getState().addCodingTask(task);
    expect(useChatStore.getState().channelTasks["ch-1"]).toHaveLength(1);
    expect(useChatStore.getState().channelTasks["ch-1"][0].instruction).toBe(
      "Fix bug",
    );
  });

  it("updates a coding task", async () => {
    const { useChatStore } = await import("@/stores/chatStore");
    const task = {
      id: "t1",
      channel_id: "ch-1",
      agent_id: "a1",
      user_id: "u1",
      instruction: "Fix bug",
      status: "pending" as const,
      result_summary: null,
      commit_sha: null,
      pr_url: null,
      branch_name: null,
      created_at: new Date().toISOString(),
      completed_at: null,
    };
    useChatStore.getState().addCodingTask(task);
    useChatStore
      .getState()
      .updateCodingTask({
        ...task,
        status: "completed",
        result_summary: "Done",
      });
    const updated = useChatStore.getState().channelTasks["ch-1"][0];
    expect(updated.status).toBe("completed");
    expect(updated.result_summary).toBe("Done");
  });

  it("toggles agent panel", async () => {
    const { useChatStore } = await import("@/stores/chatStore");
    expect(useChatStore.getState().agentPanelOpen).toBe(false);
    useChatStore.getState().setAgentPanelOpen(true);
    expect(useChatStore.getState().agentPanelOpen).toBe(true);
  });
});
