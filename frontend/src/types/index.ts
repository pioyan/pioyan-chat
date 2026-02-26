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
