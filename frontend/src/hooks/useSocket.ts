"use client";
/** useSocket hook: connect/disconnect Socket.IO and listen for events. */

import { useEffect } from "react";
import { connectSocket, disconnectSocket, getSocket } from "@/lib/socket";
import { useChatStore } from "@/stores/chatStore";
import type { CodingTask, Message } from "@/types";

export function useSocket(): void {
  const addMessage = useChatStore((s) => s.addMessage);
  const updateCodingTask = useChatStore((s) => s.updateCodingTask);

  useEffect(() => {
    connectSocket();
    const socket = getSocket();

    const handleNewMessage = (data: Message) => {
      addMessage(data);
    };

    const handleAgentResponse = (data: {
      channel_id: string;
      content: string;
    }) => {
      // Agent responses come as synthetic messages
      const msg: Message = {
        id: `agent-${Date.now()}`,
        channel_id: data.channel_id,
        sender_id: "agent",
        sender_username: "AI Agent",
        sender_avatar_url: null,
        content: data.content,
        file_url: null,
        thread_id: null,
        reply_count: 0,
        created_at: new Date().toISOString(),
        updated_at: null,
      };
      addMessage(msg);
    };

    const handleTaskStatus = (data: CodingTask) => {
      updateCodingTask(data);
    };

    socket.on("new_message", handleNewMessage);
    socket.on("agent_response", handleAgentResponse);
    socket.on("task_status", handleTaskStatus);

    return () => {
      socket.off("new_message", handleNewMessage);
      socket.off("agent_response", handleAgentResponse);
      socket.off("task_status", handleTaskStatus);
      disconnectSocket();
    };
  }, [addMessage, updateCodingTask]);
}
