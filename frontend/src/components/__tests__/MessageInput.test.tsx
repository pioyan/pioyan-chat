/**
 * Tests for MessageInput component
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock API module
vi.mock("@/lib/api", () => ({
  messagesApi: {
    post: vi.fn(),
    postThread: vi.fn(),
  },
  filesApi: {
    upload: vi.fn(),
  },
  agentsApi: {
    listByChannel: vi.fn().mockResolvedValue([]),
  },
}));

// Mock store
const mockAddMessage = vi.fn();
vi.mock("@/stores/chatStore", () => ({
  useChatStore: (selector: (s: Record<string, unknown>) => unknown) =>
    selector({ addMessage: mockAddMessage, channels: [] }),
}));

import MessageInput from "@/components/MessageInput";
import { messagesApi } from "@/lib/api";

const mockedPost = vi.mocked(messagesApi.post);
const mockedPostThread = vi.mocked(messagesApi.postThread);

describe("MessageInput", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls messagesApi.post for channel messages", async () => {
    const user = userEvent.setup();
    const mockMsg = {
      id: "msg-1",
      channel_id: "ch-1",
      sender_id: "u-1",
      sender_username: "user",
      sender_avatar_url: null,
      content: "hello",
      file_url: null,
      thread_id: null,
      reply_count: 0,
      created_at: new Date().toISOString(),
      updated_at: null,
    };
    mockedPost.mockResolvedValueOnce(mockMsg);

    render(<MessageInput channelId="ch-1" />);
    const textarea = screen.getByLabelText("メッセージ");
    await user.type(textarea, "hello");
    await user.click(screen.getByLabelText("送信"));

    expect(mockedPost).toHaveBeenCalledWith("ch-1", { content: "hello" });
    expect(mockedPostThread).not.toHaveBeenCalled();
  });

  it("calls messagesApi.postThread when threadId is provided", async () => {
    const user = userEvent.setup();
    const mockReply = {
      id: "msg-2",
      channel_id: "ch-1",
      sender_id: "u-1",
      sender_username: "user",
      sender_avatar_url: null,
      content: "reply",
      file_url: null,
      thread_id: "msg-1",
      reply_count: 0,
      created_at: new Date().toISOString(),
      updated_at: null,
    };
    mockedPostThread.mockResolvedValueOnce(mockReply);

    render(<MessageInput channelId="ch-1" threadId="msg-1" />);
    const textarea = screen.getByLabelText("メッセージ");
    await user.type(textarea, "reply");
    await user.click(screen.getByLabelText("送信"));

    expect(mockedPostThread).toHaveBeenCalledWith("msg-1", {
      content: "reply",
    });
    expect(mockedPost).not.toHaveBeenCalled();
    expect(mockAddMessage).not.toHaveBeenCalled();
  });
});
