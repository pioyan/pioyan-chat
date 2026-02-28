"use client";
/** Agent response message bubble — displayed differently from user messages. */

import {
  Bot,
  CheckCircle2,
  ExternalLink,
  GitBranch,
  GitCommitHorizontal,
  Loader2,
  XCircle,
} from "lucide-react";
import type { CodingTask } from "@/types";
import MarkdownContent from "@/components/MarkdownContent";

interface Props {
  task: CodingTask;
  agentName?: string;
}

export default function AgentMessageItem({ task, agentName }: Props) {
  const time = new Date(task.created_at).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  const displayName = agentName ?? "AI Agent";
  const isRunning = task.status === "running";

  return (
    <div
      className={`group flex gap-3 px-4 py-2 rounded-lg transition-all duration-150 border-l-2 ${
        isRunning
          ? "border-cyan-400/60 bg-cyan-50/20 dark:bg-cyan-950/10"
          : "border-transparent hover:border-violet-300/50 hover:bg-violet-50/40 dark:hover:bg-violet-950/20"
      }`}
    >
      {/* Agent avatar — pulsing ring when running */}
      <div className="mt-1 shrink-0 relative">
        {isRunning && (
          <span className="absolute inset-0 rounded-full bg-cyan-400/40 animate-ping" />
        )}
        <div
          className={`w-9 h-9 rounded-full flex items-center justify-center text-white shadow-md ring-2 ${
            isRunning
              ? "bg-gradient-to-br from-cyan-400 to-violet-500 ring-cyan-300/30"
              : "bg-gradient-to-br from-cyan-500 to-violet-500 ring-white/10 dark:ring-gray-800/30"
          }`}
        >
          <Bot size={16} />
        </div>
      </div>

      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-baseline gap-2">
          <span className="font-semibold text-sm text-violet-600 dark:text-violet-400">
            {displayName}
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-cyan-100 dark:bg-cyan-900/40 text-cyan-600 dark:text-cyan-400 font-medium">
            AI Bot
          </span>
          <span className="text-xs text-gray-400">{time}</span>
        </div>

        {/* Status + Instruction */}
        <div className="mt-1 space-y-1.5">
          {/* Status badge */}
          {isRunning && (
            <div className="inline-flex items-center gap-1.5 text-xs text-cyan-600 dark:text-cyan-400 bg-cyan-50 dark:bg-cyan-900/30 px-2 py-0.5 rounded-full border border-cyan-200/60 dark:border-cyan-700/40">
              <Loader2 size={11} className="animate-spin" />
              <span>コーディング中…</span>
            </div>
          )}
          {task.status === "completed" && (
            <div className="inline-flex items-center gap-1.5 text-xs text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/30 px-2 py-0.5 rounded-full border border-emerald-200/60 dark:border-emerald-700/40">
              <CheckCircle2 size={11} />
              <span>完了</span>
            </div>
          )}
          {task.status === "failed" && (
            <div className="inline-flex items-center gap-1.5 text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/30 px-2 py-0.5 rounded-full border border-red-200/60 dark:border-red-700/40">
              <XCircle size={11} />
              <span>失敗</span>
            </div>
          )}

          {/* Result summary */}
          {task.result_summary && (
            <div className="px-3 py-2 rounded-2xl rounded-tl-sm bg-white/70 dark:bg-gray-800/60 border border-gray-200/60 dark:border-gray-700/40 text-sm max-w-xl break-words">
              <MarkdownContent content={task.result_summary} />
            </div>
          )}

          {/* Branch + PR + commit metadata */}
          {(task.branch_name ?? task.pr_url ?? task.commit_sha) && (
            <div className="flex flex-wrap items-center gap-2 mt-1.5">
              {task.branch_name && (
                <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-800/70 border border-gray-200/60 dark:border-gray-700/40 text-gray-600 dark:text-gray-300 font-mono">
                  <GitBranch size={11} className="text-cyan-500 shrink-0" />
                  {task.branch_name}
                </span>
              )}
              {task.commit_sha && (
                <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-800/70 border border-gray-200/60 dark:border-gray-700/40 text-gray-600 dark:text-gray-300 font-mono">
                  <GitCommitHorizontal
                    size={11}
                    className="text-violet-500 shrink-0"
                  />
                  {task.commit_sha.slice(0, 7)}
                </span>
              )}
              {task.pr_url && (
                <a
                  href={task.pr_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[11px] px-2.5 py-0.5 rounded-md bg-violet-50 dark:bg-violet-900/30 border border-violet-200/60 dark:border-violet-700/40 text-violet-600 dark:text-violet-400 hover:bg-violet-100 dark:hover:bg-violet-900/50 transition-colors font-medium"
                >
                  <ExternalLink size={10} />
                  PR を表示
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
