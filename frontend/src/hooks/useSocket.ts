"use client";
/** useSocket hook: connect/disconnect Socket.IO and listen for events. */

import { useEffect } from "react";
import { connectSocket, disconnectSocket, getSocket } from "@/lib/socket";
import { useChatStore } from "@/stores/chatStore";
import type { Message } from "@/types";

export function useSocket(): void {
  const addMessage = useChatStore((s) => s.addMessage);

  useEffect(() => {
    connectSocket();
    const socket = getSocket();

    const handleNewMessage = (data: Message) => {
      addMessage(data);
    };

    socket.on("new_message", handleNewMessage);

    return () => {
      socket.off("new_message", handleNewMessage);
      disconnectSocket();
    };
  }, [addMessage]);
}
