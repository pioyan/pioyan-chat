/**
 * Tests for BotManagementPanel component (TDD — Red → Green → Refactor)
 */
import { render, screen, waitFor, within, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";

// ── Mocks ──────────────────────────────────────────────────────
const mockList = vi.fn();
const mockRegister = vi.fn();
const mockDelete = vi.fn();
const mockValidate = vi.fn();

vi.mock("@/lib/api", () => ({
  botsApi: {
    list: (...args: unknown[]) => mockList(...args),
    register: (...args: unknown[]) => mockRegister(...args),
    delete: (...args: unknown[]) => mockDelete(...args),
    validate: (...args: unknown[]) => mockValidate(...args),
  },
}));

import BotManagementPanel from "@/components/BotManagementPanel";
import type { Bot } from "@/types";

// ── Fixtures ───────────────────────────────────────────────────
const fakeBots: Bot[] = [
  {
    id: "bot-1",
    name: "build-bot",
    description: "Builds projects",
    owner_id: "u-1",
    container_file_name: "Dockerfile",
    status: "registered",
    created_at: "2026-01-01T00:00:00Z",
  },
  {
    id: "bot-2",
    name: "lint-bot",
    description: null,
    owner_id: "u-1",
    container_file_name: "Containerfile",
    status: "ready",
    created_at: "2026-01-15T00:00:00Z",
  },
];

describe("BotManagementPanel", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockList.mockResolvedValue(fakeBots);
  });

  // ── Rendering ────────────────────────────────────────────────
  it("renders the panel header", async () => {
    render(<BotManagementPanel />);
    expect(screen.getByText("ボット管理")).toBeInTheDocument();
  });

  it("shows loading state then bot list", async () => {
    render(<BotManagementPanel />);
    // wait for list to appear
    await waitFor(() => {
      expect(screen.getByText("build-bot")).toBeInTheDocument();
    });
    expect(screen.getByText("lint-bot")).toBeInTheDocument();
    expect(mockList).toHaveBeenCalledOnce();
  });

  it("shows empty state when no bots", async () => {
    mockList.mockResolvedValue([]);
    render(<BotManagementPanel />);
    await waitFor(() => {
      expect(
        screen.getByText("登録されたボットはありません"),
      ).toBeInTheDocument();
    });
  });

  it("shows bot description if present", async () => {
    render(<BotManagementPanel />);
    await waitFor(() => {
      expect(screen.getByText("Builds projects")).toBeInTheDocument();
    });
  });

  it("shows bot status badge", async () => {
    render(<BotManagementPanel />);
    await waitFor(() => {
      expect(screen.getByText("registered")).toBeInTheDocument();
      expect(screen.getByText("ready")).toBeInTheDocument();
    });
  });

  // ── Registration ─────────────────────────────────────────────
  it("opens registration form when clicking add button", async () => {
    const user = userEvent.setup();
    render(<BotManagementPanel />);
    await waitFor(() => {
      expect(screen.getByText("build-bot")).toBeInTheDocument();
    });
    const addBtn = screen.getByRole("button", { name: "ボットを登録" });
    await user.click(addBtn);
    expect(screen.getByLabelText("ボット名")).toBeInTheDocument();
    expect(screen.getByLabelText("説明")).toBeInTheDocument();
  });

  it("registers a new bot via form submission", async () => {
    const newBot: Bot = {
      id: "bot-3",
      name: "test-bot",
      description: "A test bot",
      owner_id: "u-1",
      container_file_name: "Dockerfile",
      status: "registered",
      created_at: "2026-02-01T00:00:00Z",
    };
    mockRegister.mockResolvedValue(newBot);
    // After registration, the list call returns updated list
    mockList
      .mockResolvedValueOnce(fakeBots) // initial load
      .mockResolvedValueOnce([...fakeBots, newBot]); // after register

    const user = userEvent.setup();
    render(<BotManagementPanel />);

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText("build-bot")).toBeInTheDocument();
    });

    // Open form
    await user.click(screen.getByRole("button", { name: "ボットを登録" }));

    // Fill form
    await user.type(screen.getByLabelText("ボット名"), "test-bot");
    await user.type(screen.getByLabelText("説明"), "A test bot");

    // Upload a file
    const file = new File(["FROM python:3.13-slim\nRUN pip install httpx"], "Dockerfile", {
      type: "text/plain",
    });
    fireEvent.change(screen.getByLabelText("コンテナファイル"), {
      target: { files: [file] },
    });

    // Submit
    await user.click(screen.getByRole("button", { name: "登録する" }));

    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith("test-bot", file, "A test bot");
    });

    // List should be refreshed
    await waitFor(() => {
      expect(screen.getByText("test-bot")).toBeInTheDocument();
    });
  });

  it("shows validation error when name is empty", async () => {
    const user = userEvent.setup();
    render(<BotManagementPanel />);
    await waitFor(() => {
      expect(screen.getByText("build-bot")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "ボットを登録" }));

    // Try submitting without name — file is required too
    const file = new File(["FROM node:22"], "Dockerfile", { type: "text/plain" });
    fireEvent.change(screen.getByLabelText("コンテナファイル"), {
      target: { files: [file] },
    });
    await user.click(screen.getByRole("button", { name: "登録する" }));

    expect(
      screen.getByText("ボット名は必須です"),
    ).toBeInTheDocument();
    expect(mockRegister).not.toHaveBeenCalled();
  });

  it("shows validation error when no file is selected", async () => {
    const user = userEvent.setup();
    render(<BotManagementPanel />);
    await waitFor(() => {
      expect(screen.getByText("build-bot")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "ボットを登録" }));
    await user.type(screen.getByLabelText("ボット名"), "some-bot");
    await user.click(screen.getByRole("button", { name: "登録する" }));

    expect(
      screen.getByText("コンテナファイルを選択してください"),
    ).toBeInTheDocument();
    expect(mockRegister).not.toHaveBeenCalled();
  });

  // ── Deletion ─────────────────────────────────────────────────
  it("deletes a bot when clicking delete and confirming", async () => {
    mockDelete.mockResolvedValue(undefined);
    mockList
      .mockResolvedValueOnce(fakeBots) // initial
      .mockResolvedValueOnce([fakeBots[1]]); // after delete

    // mock window.confirm
    vi.spyOn(window, "confirm").mockReturnValue(true);

    const user = userEvent.setup();
    render(<BotManagementPanel />);
    await waitFor(() => {
      expect(screen.getByText("build-bot")).toBeInTheDocument();
    });

    // Find delete button for build-bot
    const botCard = screen.getByText("build-bot").closest("[data-testid]") as HTMLElement;
    const deleteBtn = within(botCard).getByRole("button", { name: "削除" });
    await user.click(deleteBtn);

    expect(mockDelete).toHaveBeenCalledWith("bot-1");
    await waitFor(() => {
      expect(screen.queryByText("build-bot")).not.toBeInTheDocument();
    });
  });

  it("does not delete when confirm is cancelled", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);
    const user = userEvent.setup();
    render(<BotManagementPanel />);
    await waitFor(() => {
      expect(screen.getByText("build-bot")).toBeInTheDocument();
    });

    const botCard = screen.getByText("build-bot").closest("[data-testid]") as HTMLElement;
    const deleteBtn = within(botCard).getByRole("button", { name: "削除" });
    await user.click(deleteBtn);

    expect(mockDelete).not.toHaveBeenCalled();
  });

  // ── Error handling ───────────────────────────────────────────
  it("shows error message when registration fails", async () => {
    mockRegister.mockRejectedValue(new Error("Server error"));
    const user = userEvent.setup();
    render(<BotManagementPanel />);
    await waitFor(() => {
      expect(screen.getByText("build-bot")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "ボットを登録" }));
    await user.type(screen.getByLabelText("ボット名"), "fail-bot");
    const file = new File(["FROM python:3.13"], "Dockerfile", { type: "text/plain" });
    fireEvent.change(screen.getByLabelText("コンテナファイル"), {
      target: { files: [file] },
    });
    await user.click(screen.getByRole("button", { name: "登録する" }));

    await waitFor(() => {
      expect(screen.getByText(/登録に失敗しました/)).toBeInTheDocument();
    });
  });

  it("shows error message when listing fails", async () => {
    mockList.mockRejectedValue(new Error("Network error"));
    render(<BotManagementPanel />);
    await waitFor(() => {
      expect(screen.getByText(/ボット一覧の取得に失敗しました/)).toBeInTheDocument();
    });
  });
});
