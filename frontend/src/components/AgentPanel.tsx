"use client";
/** 右サイドパネル: コーディングチャンネルのエージェント管理 + タスク一覧 */

import {
  Bot,
  CheckCircle2,
  Clock,
  ExternalLink,
  GitBranch,
  Loader2,
  Plus,
  Trash2,
  X,
  XCircle,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { agentsApi, codingTasksApi } from "@/lib/api";
import { getSocket } from "@/lib/socket";
import type { Agent, CodingTask, TaskStatus } from "@/types";

interface Props {
  channelId: string;
  onClose: () => void;
}

const statusConfig: Record<
  TaskStatus,
  { icon: React.ReactNode; label: string; color: string; dot: string }
> = {
  pending: {
    icon: <Clock size={11} />,
    label: "待機中",
    color: "text-amber-500 dark:text-amber-400",
    dot: "bg-amber-400",
  },
  running: {
    icon: <Loader2 size={11} className="animate-spin" />,
    label: "実行中",
    color: "text-cyan-500 dark:text-cyan-400",
    dot: "bg-cyan-400 animate-pulse",
  },
  completed: {
    icon: <CheckCircle2 size={11} />,
    label: "完了",
    color: "text-emerald-500 dark:text-emerald-400",
    dot: "bg-emerald-400",
  },
  failed: {
    icon: <XCircle size={11} />,
    label: "失敗",
    color: "text-red-500 dark:text-red-400",
    dot: "bg-red-400",
  },
};

export default function AgentPanel({ channelId, onClose }: Props) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<CodingTask[]>([]);
  const [myAgents, setMyAgents] = useState<Agent[]>([]);
  const [showAddAgent, setShowAddAgent] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [channelAgents, channelTasks] = await Promise.all([
        agentsApi.listByChannel(channelId),
        codingTasksApi.list(channelId),
      ]);
      setAgents(channelAgents);
      setTasks(channelTasks);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [channelId]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  // ── Socket.IO: listen for real-time task status updates ────
  useEffect(() => {
    const socket = getSocket();
    if (!socket) return;

    const handleTaskStatus = (data: {
      task_id: string;
      channel_id: string;
      status: TaskStatus;
      result_summary?: string;
      commit_sha?: string;
      pr_url?: string;
      branch_name?: string;
    }) => {
      if (data.channel_id !== channelId) return;

      setTasks((prev) =>
        prev.map((t) =>
          t.id === data.task_id
            ? {
                ...t,
                status: data.status,
                result_summary: data.result_summary ?? t.result_summary,
                commit_sha: data.commit_sha ?? t.commit_sha,
                pr_url: data.pr_url ?? t.pr_url,
                branch_name: data.branch_name ?? t.branch_name,
              }
            : t,
        ),
      );
    };

    socket.on("task_status", handleTaskStatus);
    return () => {
      socket.off("task_status", handleTaskStatus);
    };
  }, [channelId]);

  const handleAddAgent = async (agentId: string) => {
    try {
      await agentsApi.assignToChannel(channelId, agentId);
      setShowAddAgent(false);
      void loadData();
    } catch {
      // ignore
    }
  };

  const handleRemoveAgent = async (agentId: string) => {
    try {
      await agentsApi.removeFromChannel(channelId, agentId);
      void loadData();
    } catch {
      // ignore
    }
  };

  const handleShowAdd = async () => {
    try {
      const allAgents = await agentsApi.list();
      const assignedIds = new Set(agents.map((a) => a.id));
      setMyAgents(allAgents.filter((a) => !assignedIds.has(a.id)));
    } catch {
      // ignore
    }
    setShowAddAgent(true);
  };

  return (
    <div className="w-80 flex flex-col h-full bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm border-l border-cyan-200/30 dark:border-cyan-700/20">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-cyan-200/30 dark:border-cyan-700/20 bg-gradient-to-r from-cyan-50/50 to-violet-50/30 dark:from-cyan-950/20 dark:to-violet-950/10">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center shadow-md shadow-cyan-500/20">
            <Bot size={14} className="text-white" />
          </div>
          <h3 className="font-semibold text-sm bg-gradient-to-r from-cyan-600 to-violet-600 dark:from-cyan-400 dark:to-violet-400 bg-clip-text text-transparent">
            エージェント & タスク
          </h3>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors rounded-lg hover:bg-gray-100/60 dark:hover:bg-gray-800/60 p-1"
          aria-label="パネルを閉じる"
        >
          <X size={14} />
        </button>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <Loader2 size={24} className="animate-spin text-violet-400" />
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          {/* Agents section */}
          <div className="px-4 pt-3 pb-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-widest">
                エージェント ({agents.length})
              </span>
              <button
                onClick={handleShowAdd}
                className="text-violet-500 hover:text-violet-600 transition-colors"
                title="エージェントを追加"
              >
                <Plus size={14} />
              </button>
            </div>
          </div>

          {agents.length === 0 ? (
            <div className="mx-4 my-2 px-3 py-3 rounded-xl border border-dashed border-gray-200/70 dark:border-gray-700/50 bg-gray-50/50 dark:bg-gray-800/20 text-center">
              <Bot
                size={22}
                className="mx-auto text-gray-300 dark:text-gray-600 mb-1"
              />
              <p className="text-xs text-gray-400 dark:text-gray-500">
                エージェントがありません
              </p>
              <p className="text-[11px] text-gray-400/70 dark:text-gray-600 mt-0.5">
                + ボタンで割り当てしてください
              </p>
            </div>
          ) : (
            <div className="px-2">
              {agents.map((agent) => (
                <div
                  key={agent.id}
                  className="flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-violet-50/50 dark:hover:bg-violet-950/20 group"
                >
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white text-xs font-bold shrink-0">
                    <Bot size={12} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">
                      {agent.name}
                    </p>
                    {agent.description && (
                      <p className="text-xs text-gray-400 truncate">
                        {agent.description}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => handleRemoveAgent(agent.id)}
                    className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all"
                    title="エージェントを除外"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Add agent inline panel */}
          {showAddAgent && (
            <div className="mx-3 mt-2 rounded-xl border border-cyan-200/50 dark:border-cyan-700/30 bg-cyan-50/40 dark:bg-cyan-950/20 overflow-hidden">
              <div className="flex items-center justify-between px-3 py-2 border-b border-cyan-200/40 dark:border-cyan-700/30">
                <span className="text-xs font-semibold text-cyan-700 dark:text-cyan-400">
                  エージェントを追加
                </span>
                <button
                  onClick={() => setShowAddAgent(false)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
                >
                  <X size={12} />
                </button>
              </div>
              <div className="py-1">
                {myAgents.length === 0 ? (
                  <p className="text-xs text-gray-400 px-3 py-2">
                    追加可能なエージェントがありません
                  </p>
                ) : (
                  myAgents.map((agent) => (
                    <button
                      key={agent.id}
                      onClick={() => handleAddAgent(agent.id)}
                      className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-cyan-100/60 dark:hover:bg-cyan-900/30 transition-colors"
                    >
                      <div className="w-5 h-5 rounded-full bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center shrink-0">
                        <Bot size={10} className="text-white" />
                      </div>
                      <span className="flex-1 truncate font-medium">
                        {agent.name}
                      </span>
                      {agent.description && (
                        <span className="text-xs text-gray-400 truncate">
                          {agent.description}
                        </span>
                      )}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Tasks section */}
          <div className="px-4 pt-4 pb-1">
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-widest">
              タスク履歴 ({tasks.length})
            </span>
          </div>

          {tasks.length === 0 ? (
            <div className="mx-4 my-2 px-3 py-4 rounded-xl border border-dashed border-gray-200/70 dark:border-gray-700/50 bg-gray-50/50 dark:bg-gray-800/20 text-center">
              <Clock
                size={22}
                className="mx-auto text-gray-300 dark:text-gray-600 mb-1"
              />
              <p className="text-xs text-gray-400 dark:text-gray-500">
                まだタスクがありません
              </p>
              <p className="text-[11px] text-gray-400/70 dark:text-gray-600 mt-0.5">
                @エージェント名 でタスクを送信しましょう
              </p>
            </div>
          ) : (
            <div className="px-3 pb-4">
              {/* Timeline */}
              <div className="relative pl-4 border-l-2 border-gray-200/60 dark:border-gray-700/40 space-y-0.5">
                {tasks.map((task) => {
                  const st = statusConfig[task.status];
                  return (
                    <div
                      key={task.id}
                      className="relative pt-2 pb-2 pr-1 pl-4 rounded-r-lg hover:bg-gray-50/70 dark:hover:bg-gray-800/30 transition-colors group/task"
                    >
                      {/* Timeline dot */}
                      <span
                        className={`absolute -left-[17px] top-3.5 w-2.5 h-2.5 rounded-full border-2 border-white dark:border-gray-900 ${st.dot}`}
                      />

                      {/* Status + time */}
                      <div className="flex items-center gap-1.5 mb-0.5">
                        <span
                          className={`flex items-center gap-1 text-[11px] font-medium ${st.color}`}
                        >
                          {st.icon}
                          {st.label}
                        </span>
                        <span className="text-[11px] text-gray-400 ml-auto">
                          {new Date(task.created_at).toLocaleString([], {
                            month: "short",
                            day: "numeric",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      </div>

                      {/* Instruction */}
                      <p className="text-xs text-gray-600 dark:text-gray-300 line-clamp-2 leading-relaxed">
                        {task.instruction}
                      </p>

                      {/* Metadata */}
                      {(task.branch_name ?? task.pr_url) && (
                        <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
                          {task.branch_name && (
                            <span className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-500 font-mono border border-gray-200/60 dark:border-gray-700/40">
                              <GitBranch size={9} className="text-cyan-500" />
                              {task.branch_name}
                            </span>
                          )}
                          {task.pr_url && (
                            <a
                              href={task.pr_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded bg-violet-50 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400 hover:bg-violet-100 dark:hover:bg-violet-900/50 transition-colors border border-violet-200/50 dark:border-violet-700/40"
                            >
                              <ExternalLink size={9} />
                              PR
                            </a>
                          )}
                        </div>
                      )}

                      {/* Result summary */}
                      {task.result_summary && (
                        <p className="mt-1 text-[11px] text-gray-400 line-clamp-2 italic">
                          {task.result_summary}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
