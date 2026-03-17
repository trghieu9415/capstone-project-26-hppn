import { QueryRequestDTO } from "@/types/chat";
import apiClient from "./_client";

export const chatService = {
  ask: async (data: QueryRequestDTO): Promise<string[]> => {
    const response = await apiClient.post("/api/query/ask", data);
    return response.data;
  },

  askStream: async (data: QueryRequestDTO, onChunk: (text: string) => void): Promise<void> => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";

    const response = await fetch(`${baseUrl}/api/query/ask`, {
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

    while (!done) {
      const { value, done: readerDone } = await reader.read();
      done = readerDone;
      if (value) {
        const chunk = decoder.decode(value, { stream: true });
        onChunk(chunk);
      }
    }
  },
};
