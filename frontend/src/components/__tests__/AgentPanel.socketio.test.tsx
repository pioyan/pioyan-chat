/**
 * Tests for AgentPanel Socket.IO real-time task_status event handling.
 *
 * Verifies that when a `task_status` event arrives via Socket.IO,
 * the AgentPanel updates task status in the UI in real-time.
 */
import { render, screen, waitFor, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

// ── Socket.IO mock ─────────────────────────────────────────────

type EventHandler = (...args: unknown[]) => void;
const handlers: Record<string, EventHandler[]> = {};

const mockSocket = {
  on: vi.fn((event: string, handler: EventHandler) => {
    if (!handlers[event]) handlers[event] = [];
    handlers[event].push(handler);
  }),
  off: vi.fn((event: string, handler: EventHandler) => {
    if (handlers[event]) {
      handlers[event] = handlers[event].filter((h) => h !== handler);
    }
  }),
  connected: true,
};

function emitMockEvent(event: string, data: unknown) {
  for (const h of handlers[event] ?? []) {
    h(data);
  }
}

vi.mock("@/lib/socket", () => ({
  getSocket: () => mockSocket,
}));

// ── API mocks ──────────────────────────────────────────────────

vi.mock("@/lib/api", () => ({
  agentsApi: {
    list: vi.fn().mockResolvedValue([]),
    listByChannel: vi.fn().mockResolvedValue([
      {
        id: "agent-1",
        name: "code-bot",
        description: "A coding bot",
        system_prompt: null,
        source: "manual",
        repo_agent_path: null,
        status: "ready",
        owner_id: "u-1",
        created_at: "2026-01-01T00:00:00Z",
      },
    ]),
    assignToChannel: vi.fn(),
    removeFromChannel: vi.fn(),
  },
  codingTasksApi: {
    list: vi.fn().mockResolvedValue([
      {
        id: "task-1",
        channel_id: "ch-coding-1",
        agent_id: "agent-1",
        user_id: "u-1",
        instruction: "Build auth module",
        status: "running",
        result_summary: null,
        commit_sha: null,
        pr_url: null,
        branch_name: null,
        created_at: "2026-02-28T10:00:00Z",
        completed_at: null,
      },
    ]),
  },
}));

import AgentPanel from "@/components/AgentPanel";

describe("AgentPanel — Socket.IO task_status", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset event handlers
    for (const key of Object.keys(handlers)) {
      delete handlers[key];
    }
  });

  it("registers task_status event listener on mount", async () => {
    render(
      <AgentPanel channelId="ch-coding-1" onClose={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByText("Build auth module")).toBeInTheDocument();
    });

    // Verify socket.on was called with "task_status"
    expect(mockSocket.on).toHaveBeenCalledWith(
      "task_status",
      expect.any(Function),
    );
  });

  it("updates task status from running to completed via Socket.IO event", async () => {
    render(
      <AgentPanel channelId="ch-coding-1" onClose={vi.fn()} />,
    );

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText("Build auth module")).toBeInTheDocument();
    });

    // Verify initial state shows "実行中" (running)
    expect(screen.getByText("実行中")).toBeInTheDocument();

    // Simulate task_status Socket.IO event: running → completed
    act(() => {
      emitMockEvent("task_status", {
        task_id: "task-1",
        channel_id: "ch-coding-1",
        status: "completed",
        result_summary: "Created auth module with 5 files",
        commit_sha: "abc123",
        pr_url: "https://github.com/pioyan/talent-flow/pull/42",
        branch_name: "agent/code-bot/abc123",
      });
    });

    // Verify UI updated to show "完了" (completed)
    await waitFor(() => {
      expect(screen.getByText("完了")).toBeInTheDocument();
    });

    // Verify result details appear
    expect(
      screen.getByText("Created auth module with 5 files"),
    ).toBeInTheDocument();

    // Verify branch and PR link
    expect(screen.getByText("agent/code-bot/abc123")).toBeInTheDocument();
    expect(screen.getByText("PR")).toBeInTheDocument();
  });

  it("updates task status from running to failed via Socket.IO event", async () => {
    render(
      <AgentPanel channelId="ch-coding-1" onClose={vi.fn()} />,
    );

    await waitFor(() => {
      expect(screen.getByText("Build auth module")).toBeInTheDocument();
    });

    // Simulate failure event
    act(() => {
      emitMockEvent("task_status", {
        task_id: "task-1",
        channel_id: "ch-coding-1",
        status: "failed",
        result_summary: "Docker daemon not running",
      });
    });

    await waitFor(() => {
      expect(screen.getByText("失敗")).toBeInTheDocument();
    });
    expect(
      screen.getByText("Docker daemon not running"),
    ).toBeInTheDocument();
  });

  it("ignores task_status events for other channels", async () => {
    render(
      <AgentPanel channelId="ch-coding-1" onClose={vi.fn()} />,
    );

    await waitFor(() => {
      expect(screen.getByText("Build auth module")).toBeInTheDocument();
    });

    // Simulate event for a different channel
    act(() => {
      emitMockEvent("task_status", {
        task_id: "task-1",
        channel_id: "ch-OTHER-999",
        status: "completed",
        result_summary: "Should not appear",
      });
    });

    // Should still show original "実行中" status
    expect(screen.getByText("実行中")).toBeInTheDocument();
    expect(
      screen.queryByText("Should not appear"),
    ).not.toBeInTheDocument();
  });

  it("unregisters event listener on unmount", async () => {
    const { unmount } = render(
      <AgentPanel channelId="ch-coding-1" onClose={vi.fn()} />,
    );

    await waitFor(() => {
      expect(screen.getByText("Build auth module")).toBeInTheDocument();
    });

    unmount();

    expect(mockSocket.off).toHaveBeenCalledWith(
      "task_status",
      expect.any(Function),
    );
  });
});
