import { QueryRequestDTO } from "@/types/chat";
import { createParser } from "eventsource-parser";
import apiClient from "./_client";

export const chatService = {
  ask: async (data: QueryRequestDTO): Promise<string> => {
    const response = await apiClient.post("/api/query/ask", data);
    return response.data;
  },

  askStream: async (data: QueryRequestDTO, onChunk: (text: string) => void): Promise<void> => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const baseUrl = "http://localhost:8080";

    const response = await fetch(`${baseUrl}/api/query/ask/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(data),
    });

    if (!response.body) throw new Error("ReadableStream not supported in this browser.");

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let done = false;
    let fullContent = "";

    const parser = createParser({
      onEvent: (event) => {
        const eventType = event.event || "message";

        if (eventType === "message") {
          if (event.data === "[DONE]") {
            done = true;
            return;
          }

          fullContent += event.data;

          if (typeof onChunk === "function") {
            onChunk(event.data);
          }
        }
      },
      onError: (error) => {
        console.error("Lỗi từ parser:", error);
      },
    });

    while (!done) {
      const { value, done: readerDone } = await reader.read();

      if (readerDone) {
        break;
      }

      if (value) {
        const chunk = decoder.decode(value, { stream: true });
        parser.feed(chunk);
      }
    }
    console.log("Toàn bộ nội dung:", fullContent);
  },
};
