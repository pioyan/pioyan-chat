/** Shared TypeScript types for pioyan-chat frontend. */

export interface User {
  id: string;
  username: string;
  email: string;
  avatar_url: string | null;
  created_at: string;
}

export interface Channel {
  id: string;
  name: string;
  description: string | null;
  is_private: boolean;
  is_direct: boolean;
  is_coding: boolean;
  members: string[];
  // Coding channel fields
  repo_url: string | null;
  repo_owner: string | null;
  repo_name: string | null;
  default_branch: string;
  assigned_agents: string[];
  created_by: string;
  created_at: string;
}

export interface Message {
  id: string;
  channel_id: string;
  sender_id: string;
  sender_username: string;
  sender_avatar_url: string | null;
  content: string;
  file_url: string | null;
  thread_id: string | null;
  reply_count: number;
  created_at: string;
  updated_at: string | null;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
}

export interface Bot {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  container_file_name: string;
  status: "registered" | "building" | "ready" | "error";
  created_at: string;
}

export interface BotValidateResponse {
  valid: boolean;
  errors: string[];
}

// ── AI Agent types ───────────────────────────────────────────

export type AgentSource = "repo" | "manual";
export type AgentStatus = "registered" | "ready" | "error";

export interface Agent {
  id: string;
  name: string;
  description: string | null;
  system_prompt: string | null;
  source: AgentSource;
  repo_agent_path: string | null;
  status: AgentStatus;
  owner_id: string;
  created_at: string;
}

export type ContainerStatus = "creating" | "running" | "stopped" | "error";

export interface AgentContainer {
  id: string;
  agent_id: string;
  channel_id: string;
  container_id: string | null;
  status: ContainerStatus;
  repo_branch: string | null;
  created_at: string;
  last_active_at: string | null;
}

export type TaskStatus = "pending" | "running" | "completed" | "failed";

export interface CodingTask {
  id: string;
  channel_id: string;
  agent_id: string;
  user_id: string;
  instruction: string;
  status: TaskStatus;
  result_summary: string | null;
  commit_sha: string | null;
  pr_url: string | null;
  branch_name: string | null;
  created_at: string;
  completed_at: string | null;
}
