import { create } from "zustand";
import { QueryRequestDTO } from "@/types/chat";
import { chatService } from "@/services/chatService";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface ChatState {
  messages: ChatMessage[];
  isReceiving: boolean;
  error: string | null;

  askQuestion: (request: QueryRequestDTO) => Promise<void>;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isReceiving: false,
  error: null,

  askQuestion: async (request: QueryRequestDTO) => {
    const userMessageId = crypto.randomUUID();
    const assistantMessageId = crypto.randomUUID();

    set((state) => ({
      isReceiving: true,
      error: null,
      messages: [
        ...state.messages,
        { id: userMessageId, role: "user", content: request.question || "" },
        { id: assistantMessageId, role: "assistant", content: "" }, // Khởi tạo tin nhắn rỗng chờ stream
      ],
    }));

    try {
      await chatService.askStream(request, (chunk: string) => {
        set((state) => {
          const updatedMessages = state.messages.map((msg) => {
            if (msg.id === assistantMessageId) {
              return { ...msg, content: msg.content + chunk };
            }
            return msg;
          });
          return { messages: updatedMessages };
        });
      });

      set({ isReceiving: false });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi phản hồi từ AI Engine";
      set((state) => ({
        error: errorMessage,
        isReceiving: false,
        messages: state.messages.map((msg) =>
          msg.id === assistantMessageId ? { ...msg, content: `[Lỗi hệ thống]: ${errorMessage}` } : msg
        ),
      }));
    }
  },

  clearChat: () => {
    set({ messages: [], error: null, isReceiving: false });
  },
}));
