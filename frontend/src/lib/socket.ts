"use client";
/** Socket.IO client singleton. */

import { io, Socket } from "socket.io-client";
import { getToken } from "./auth";

const SOCKET_URL =
  process.env.NEXT_PUBLIC_SOCKET_URL ?? "http://localhost:8000";

let socket: Socket | null = null;

export function getSocket(): Socket {
  if (!socket) {
    const token = getToken();
    socket = io(SOCKET_URL, {
      auth: { token },
      transports: ["websocket"],
      autoConnect: false,
    });
  }
  return socket;
}

export function connectSocket(): void {
  const s = getSocket();
  if (!s.connected) {
    s.connect();
  }
}

export function disconnectSocket(): void {
  if (socket?.connected) {
    socket.disconnect();
  }
  socket = null;
}

export function joinChannel(channelId: string): void {
  getSocket().emit("join_channel", { channel_id: channelId });
}

export function leaveChannel(channelId: string): void {
  getSocket().emit("leave_channel", { channel_id: channelId });
}

export function sendMessage(channelId: string, content: string): void {
  getSocket().emit("new_message", { channel_id: channelId, content });
}

export function emitTyping(channelId: string): void {
  getSocket().emit("typing", { channel_id: channelId });
}
