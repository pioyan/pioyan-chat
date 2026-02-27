/**
 * Tests for MessageItem component
 */
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import MessageItem from "@/components/MessageItem";

const mockMessage = {
  id: "msg-1",
  channel_id: "ch-1",
  sender_id: "user-1",
  sender_username: "testuser",
  sender_avatar_url: null,
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

  it("shows hover reply button for root messages", () => {
    render(<MessageItem message={mockMessage} onThreadClick={vi.fn()} />);
    expect(screen.getByLabelText("スレッドで返信")).toBeInTheDocument();
  });

  it("does not show hover reply button for thread reply messages", () => {
    render(
      <MessageItem
        message={{ ...mockMessage, thread_id: "parent-1" }}
        onThreadClick={vi.fn()}
      />,
    );
    expect(screen.queryByLabelText("スレッドで返信")).not.toBeInTheDocument();
  });

  it("calls onThreadClick when hover reply button is clicked", async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();
    render(<MessageItem message={mockMessage} onThreadClick={handleClick} />);
    await user.click(screen.getByLabelText("スレッドで返信"));
    expect(handleClick).toHaveBeenCalledWith("msg-1");
  });
});
