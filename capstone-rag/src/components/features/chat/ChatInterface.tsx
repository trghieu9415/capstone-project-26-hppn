import React, { useEffect, useRef } from "react";
import { Send, RotateCcw, Filter, Square, MessageSquare } from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import ReactMarkdown from "react-markdown";
import { ContextFilters } from "./ContextFilters";
import { useDocumentStore } from "@/stores/useDocumentStore";
import { useUIStore } from "@/stores/useUIStore";
import { useChatStore } from "@/stores/useChatStore";
import { cn } from "@/lib/utils";

export const ChatInterface: React.FC = () => {
  const { messages, input, isReceiving, askQuestion, stopStreaming, setInput } = useChatStore();
  const { openDialog, showFilters, setShowFilters } = useUIStore();
  const { filters } = useDocumentStore();

  const scrollRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = () => {
    if (!input.trim() || isReceiving) return;
    askQuestion({ question: input, docIds: filters.docIds, folderIds: filters.folderIds, tagIds: filters.tagIds });
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col bg-white relative overflow-hidden">
      {/* Header */}
      <header className="h-20 border-b border-slate-100 flex items-center justify-between px-8 shrink-0 bg-white/80 backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-50 rounded-2xl flex items-center justify-center">
            <MessageSquare className="text-blue-600" size={20} />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-800">UniRAG Assistant</h2>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-[10px] font-bold text-emerald-600 uppercase tracking-widest">AI Online</span>
            </div>
          </div>
        </div>

        <button
          onClick={() => openDialog("clear-chat")}
          className="p-2.5 hover:bg-slate-100 rounded-2xl text-slate-400 hover:text-slate-600 transition-all group"
          title="Làm mới cuộc hội thoại"
        >
          <RotateCcw size={20} className="group-hover:-rotate-45 transition-transform" />
        </button>
      </header>

      {/* Messages List */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-8 scroll-smooth custom-scrollbar">
        {messages.map((msg) => (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            key={msg.id}
            className={cn("flex gap-4 max-w-4xl mx-auto", msg.role === "user" ? "flex-row-reverse" : "flex-row")}
          >
            <div
              className={cn(
                "w-8 h-8 rounded-lg flex items-center justify-center shrink-0 shadow-sm",
                msg.role === "user" ? "bg-slate-800 text-white" : "bg-blue-600 text-white"
              )}
            >
              {msg.role === "user" ? "U" : "AI"}
            </div>
            <div className={cn("flex flex-col space-y-1", msg.role === "user" ? "items-end" : "items-start")}>
              <div
                className={cn(
                  "px-4 py-3 rounded-2xl text-sm shadow-sm",
                  msg.role === "user"
                    ? "bg-blue-600 text-white rounded-tr-none"
                    : "bg-slate-100 text-slate-800 rounded-tl-none border border-slate-200"
                )}
              >
                <div className="markdown-body">
                  {msg.content ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : msg.isStreaming ? (
                    <div className="flex gap-1 py-1">
                      <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                      <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                      <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" />
                    </div>
                  ) : null}
                  {msg.isStreaming && msg.content && (
                    <span className="inline-block w-1.5 h-4 bg-blue-400 ml-1 animate-pulse align-middle" />
                  )}
                </div>
              </div>
              <span className="text-[10px] text-slate-400 font-medium px-1 uppercase">
                {msg.role === "user" ? "Bạn" : "UniRAG Assistant"}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Input Area */}
      <div className="p-6 bg-linear-to-t from-white via-white to-transparent">
        <div className="max-w-4xl mx-auto relative">
          <AnimatePresence>{showFilters && <ContextFilters />}</AnimatePresence>

          <div className="flex relative group">
            <div className="relative w-full border border-slate-300 rounded-xl bg-white shadow-sm focus-within:ring-2 focus-within:ring-blue-500 transition-all">
              <textarea
                // Cấu hình để textarea giới hạn ~5 dòng và cuộn
                className="w-full resize-none bg-transparent outline-none p-3 pb-14 min-h-[48px] max-h-[120px] overflow-y-auto rounded-xl text-slate-700"
                placeholder="Nhập tin nhắn..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                // Nếu bro muốn nó tự động co giãn chiều cao khi gõ (auto-resize),
                // bro có thể tham khảo thư viện 'react-textarea-autosize'.
                // Còn nếu chỉ dùng HTML thuần thì code này sẽ fix cứng khung hiển thị ở max 5 dòng.
              />

              {/* Cụm 2 nút của bro giữ nguyên */}
              <div className="absolute right-2 bottom-2 flex items-center gap-2">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={cn(
                    "p-2 rounded-xl transition-all",
                    showFilters ? "bg-blue-100 text-blue-600" : "text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                  )}
                  title="Bộ lọc ngữ cảnh"
                >
                  <Filter size={20} />
                </button>

                {isReceiving ? (
                  <button
                    onClick={stopStreaming}
                    className="p-2 bg-red-100 text-red-600 rounded-xl hover:bg-red-200 transition-all shadow-sm shadow-red-100"
                    title="Dừng trả lời"
                  >
                    <Square size={20} fill="currentColor" />
                  </button>
                ) : (
                  <button
                    onClick={handleSendMessage}
                    disabled={!input.trim()}
                    className="p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:bg-slate-300 transition-all shadow-lg shadow-blue-200"
                    title="Gửi tin nhắn"
                  >
                    <Send size={20} />
                  </button>
                )}
              </div>
            </div>
          </div>

          <p className="text-[10px] text-center text-slate-400 mt-3 font-medium">
            AI có thể đưa ra thông tin chưa chính xác. Vui lòng kiểm tra lại các quy chế chính thức.
          </p>
        </div>
      </div>
    </div>
  );
};
