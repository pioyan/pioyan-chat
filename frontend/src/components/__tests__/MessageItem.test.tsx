/**
 * Tests for MessageItem component
 */
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import MessageItem from "@/components/MessageItem";

const mockMessage = {
  id: "msg-1",
  channel_id: "ch-1",
  sender_id: "user-1",
  content: "Hello, world!",
  file_url: null,
  thread_id: null,
  reply_count: 0,
  created_at: "2026-01-01T12:00:00Z",
  updated_at: null,
};

describe("MessageItem", () => {
  it("renders message content", () => {
    render(<MessageItem message={mockMessage} onThreadClick={vi.fn()} />);
    expect(screen.getByText("Hello, world!")).toBeInTheDocument();
  });

  it("renders file link when file_url is set", () => {
    render(
      <MessageItem
        message={{ ...mockMessage, file_url: "/uploads/test.png" }}
        onThreadClick={vi.fn()}
      />,
    );
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("href", "/uploads/test.png");
  });

  it("shows reply count badge when reply_count > 0", () => {
    render(
      <MessageItem
        message={{ ...mockMessage, reply_count: 3 }}
        onThreadClick={vi.fn()}
      />,
    );
    expect(screen.getByText(/3/)).toBeInTheDocument();
  });

  it("does not show reply badge when reply_count is 0", () => {
    render(<MessageItem message={mockMessage} onThreadClick={vi.fn()} />);
    expect(screen.queryByText(/replies/)).not.toBeInTheDocument();
  });
});
