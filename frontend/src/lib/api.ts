/** Typed API client for pioyan-chat backend. */

import type { AuthTokenResponse, Channel, Message, User } from "@/types";
import { getToken } from "./auth";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

// ── Auth ──────────────────────────────────────────────────────
export const authApi = {
  signup: (data: { username?: string; email: string; password: string }) =>
    request<AuthTokenResponse>("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (data: { email: string; password: string }) =>
    request<AuthTokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  me: () => request<User>("/api/auth/me"),

  updateMe: (data: { username?: string; avatar_url?: string }) =>
    request<User>("/api/auth/me", {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  uploadAvatar: async (file: File) => {
    const token = getToken();
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${BASE_URL}/api/auth/me/avatar`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(res.status, body.detail ?? res.statusText);
    }
    return res.json() as Promise<User>;
  },
};

// ── Channels ──────────────────────────────────────────────────
export const channelsApi = {
  list: () => request<Channel[]>("/api/channels"),
  get: (id: string) => request<Channel>(`/api/channels/${id}`),
  create: (data: {
    name: string;
    description?: string;
    is_private?: boolean;
  }) =>
    request<Channel>("/api/channels", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  update: (id: string, data: { name?: string; description?: string }) =>
    request<Channel>(`/api/channels/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  delete: (id: string) =>
    request<void>(`/api/channels/${id}`, { method: "DELETE" }),
  addMember: (id: string, userId: string) =>
    request<Channel>(`/api/channels/${id}/members`, {
      method: "POST",
      body: JSON.stringify({ user_id: userId }),
    }),
  removeMember: (id: string, userId: string) =>
    request<Channel>(`/api/channels/${id}/members/${userId}`, {
      method: "DELETE",
    }),
};

// ── Messages ─────────────────────────────────────────────────
export const messagesApi = {
  list: (channelId: string, params?: { limit?: number; before?: string }) => {
    const qs = new URLSearchParams();
    if (params?.limit) qs.set("limit", String(params.limit));
    if (params?.before) qs.set("before", params.before);
    const query = qs.toString() ? `?${qs}` : "";
    return request<Message[]>(`/api/channels/${channelId}/messages${query}`);
  },
  post: (channelId: string, data: { content: string; file_url?: string }) =>
    request<Message>(`/api/channels/${channelId}/messages`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  delete: (id: string) =>
    request<void>(`/api/messages/${id}`, { method: "DELETE" }),
  search: (q: string) =>
    request<Message[]>(`/api/messages/search?q=${encodeURIComponent(q)}`),
  getThread: (id: string) => request<Message[]>(`/api/messages/${id}/thread`),
  postThread: (id: string, data: { content: string }) =>
    request<Message>(`/api/messages/${id}/thread`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

// ── DM ────────────────────────────────────────────────────────
export const dmApi = {
  list: () => request<Channel[]>("/api/dm"),
  start: (userId: string) =>
    request<Channel>("/api/dm", {
      method: "POST",
      body: JSON.stringify({ user_id: userId }),
    }),
  messages: (conversationId: string) =>
    request<Message[]>(`/api/dm/${conversationId}/messages`),
};

// ── Files ─────────────────────────────────────────────────────
export const filesApi = {
  upload: async (file: File) => {
    const token = getToken();
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${BASE_URL}/api/files/upload`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(res.status, body.detail ?? res.statusText);
    }
    return res.json() as Promise<{
      filename: string;
      file_url: string;
      size: number;
    }>;
  },
};

export { ApiError };
