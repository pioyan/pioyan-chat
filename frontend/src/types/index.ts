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
  members: string[];
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
