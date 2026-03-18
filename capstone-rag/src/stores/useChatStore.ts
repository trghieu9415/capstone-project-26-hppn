import { create } from "zustand";
import { chatService } from "@/services/chatService";
import { Message } from "@/types/chat";

export interface QueryRequestDTO {
  question?: string;
  docIds?: string[];
  folderIds?: string[];
  tagIds?: string[];
}

interface ChatState {
  messages: Message[];
  isReceiving: boolean;
  error: string | null;
  input: string;

  // Methods
  setInput: (input: string) => void;
  askQuestionStream: (request: QueryRequestDTO) => Promise<void>;
  askQuestion: (request: QueryRequestDTO) => Promise<void>;
  stopStreaming: () => void;
  clearChat: () => void;
}

const INITIAL_WELCOME_MSG: Message = {
  id: "welcome",
  role: "assistant",
  content: "Chào mừng bạn đến với **UniRAG SGU**! Tôi có thể giúp gì cho bạn?",
};

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [INITIAL_WELCOME_MSG],
  isReceiving: false,
  error: null,
  input: "",

  setInput: (input) => set({ input }),

  stopStreaming: () => set({ isReceiving: false }),

  clearChat: () => {
    set({
      messages: [{ ...INITIAL_WELCOME_MSG, id: Date.now().toString() }],
      error: null,
      isReceiving: false,
      input: "",
    });
  },

  askQuestionStream: async (request: QueryRequestDTO) => {
    const { isReceiving, messages } = get();
    const questionText = request.question?.trim();

    if (!questionText || isReceiving) return;

    const userMessageId = crypto.randomUUID();
    const assistantMessageId = crypto.randomUUID();

    set({
      isReceiving: true,
      error: null,
      input: "",
      messages: [
        ...messages,
        { id: userMessageId, role: "user", content: questionText },
        { id: assistantMessageId, role: "assistant", content: "", isStreaming: true },
      ],
    });

    try {
      await chatService.askStream(request, (chunk: string) => {
        if (!get().isReceiving) return;

        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === assistantMessageId ? { ...msg, content: msg.content + chunk } : msg
          ),
        }));
      });

      set((state) => ({
        isReceiving: false,
        messages: state.messages.map((msg) => (msg.id === assistantMessageId ? { ...msg, isStreaming: false } : msg)),
      }));
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi phản hồi từ AI Engine";
      set((state) => ({
        error: errorMessage,
        isReceiving: false,
        messages: state.messages.map((msg) =>
          msg.id === assistantMessageId
            ? { ...msg, content: msg.content + `\n\n[Lỗi hệ thống]: ${errorMessage}`, isStreaming: false }
            : msg
        ),
      }));
    }
  },

  askQuestion: async (request: QueryRequestDTO) => {
    const { isReceiving, messages } = get();
    const questionText = request.question?.trim();

    if (!questionText || isReceiving) return;

    const userMessageId = crypto.randomUUID();
    const assistantMessageId = crypto.randomUUID();

    set({
      isReceiving: true,
      error: null,
      input: "",
      messages: [
        ...messages,
        { id: userMessageId, role: "user", content: questionText },
        { id: assistantMessageId, role: "assistant", content: "", isStreaming: true },
      ],
    });

    try {
      const fullResponse = await chatService.ask(request);

      if (!get().isReceiving) return;
      const speedMs = 15;
      const chunkSize = 3;
      let currentIndex = 0;

      const typingInterval = setInterval(() => {
        if (!get().isReceiving || currentIndex >= fullResponse.length) {
          clearInterval(typingInterval);

          set((state) => ({
            isReceiving: false,
            messages: state.messages.map((msg) =>
              msg.id === assistantMessageId ? { ...msg, content: fullResponse, isStreaming: false } : msg
            ),
          }));
          return;
        }

        currentIndex += chunkSize;
        const currentText = fullResponse.slice(0, currentIndex);

        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === assistantMessageId ? { ...msg, content: currentText } : msg
          ),
        }));
      }, speedMs);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi phản hồi từ AI Engine";
      set((state) => ({
        error: errorMessage,
        isReceiving: false,
        messages: state.messages.map((msg) =>
          msg.id === assistantMessageId
            ? { ...msg, content: `[Lỗi hệ thống]: ${errorMessage}`, isStreaming: false }
            : msg
        ),
      }));
    }
  },
}));
