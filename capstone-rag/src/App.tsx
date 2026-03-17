import React, { useState, useEffect, useRef } from "react";
import {
  Folder as FolderIcon,
  FileText,
  Tag as TagIcon,
  Plus,
  Trash2,
  Edit2,
  Upload,
  Send,
  Square,
  Filter,
  X,
  MessageSquare,
  RotateCcw,
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import ReactMarkdown from "react-markdown";
import { cn } from "./lib/utils";
import { Folder, Document, Tag, Message, ContextFilters, DialogState } from "./types";
import { Dialog } from "./components/Dialog";
import { FolderNode } from "./components/FolderNode";
import { TreeSelectNode } from "./components/TreeSelectNode";
import { INITIAL_FOLDERS, INITIAL_DOCS, INITIAL_TAGS } from "./mock/mocks";

export default function App() {
  // State
  const [activeTab, setActiveTab] = useState<"folders" | "documents" | "tags">("folders");
  const [folders, setFolders] = useState<Folder[]>(INITIAL_FOLDERS);
  const [documents, setDocuments] = useState<Document[]>(INITIAL_DOCS);
  const [tags, setTags] = useState<Tag[]>(INITIAL_TAGS);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Chào mừng bạn đến với **UniRAG SGU**! Tôi có thể giúp gì cho bạn về các quy chế học vụ?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [filters, setFilters] = useState<ContextFilters>({
    docIds: [],
    folderIds: [],
    tagIds: [],
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null);
  const isStreamingRef = useRef(false);

  // Dialog States
  const [dialogConfig, setDialogConfig] = useState<{
    type: DialogState;
    data?: any;
  }>({ type: null });
  const [dialogInputValue, setDialogInputValue] = useState("");
  const [dialogSelectedFolderId, setDialogSelectedFolderId] = useState<string | null>(null);
  const [dialogSelectedTagIds, setDialogSelectedTagIds] = useState<string[]>([]);

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  // --- Handlers ---

  const handleSendMessage = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsStreaming(true);
    isStreamingRef.current = true;

    // Mock SSE Streaming
    const assistantId = (Date.now() + 1).toString();
    setMessages((prev) => [...prev, { id: assistantId, role: "assistant", content: "", isStreaming: true }]);

    // Simulated "Thinking" delay
    await new Promise((resolve) => setTimeout(resolve, 1500));
    if (!isStreamingRef.current) return; // Check if user stopped during thinking

    const fullResponse =
      "Dựa trên quy chế đào tạo của SGU, sinh viên cần hoàn thành tối thiểu 120 tín chỉ đối với hệ cử nhân. Bạn có thể tra cứu chi tiết tại thư mục 'Quy chế đào tạo' hoặc xem tài liệu 'Quy che hoc vu SGU 2023'. Ngoài ra, các biểu mẫu xin thôi học hoặc tạm dừng học tập có sẵn trong tab 'Tài liệu'.";
    const words = fullResponse.split(" ");
    let currentContent = "";

    for (let i = 0; i < words.length; i++) {
      if (!isStreamingRef.current) break;

      await new Promise((resolve) => setTimeout(resolve, 30 + Math.random() * 40));
      currentContent += words[i] + " ";

      setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, content: currentContent } : m)));
    }

    setMessages((prev) => prev.map((m) => (m.id === assistantId ? { ...m, isStreaming: false } : m)));
    setIsStreaming(false);
    isStreamingRef.current = false;
  };

  const handleStopStreaming = () => {
    setIsStreaming(false);
    isStreamingRef.current = false;
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: Date.now().toString(),
        role: "assistant",
        content: "Chào mừng bạn đến với **UniRAG SGU**! Tôi có thể giúp gì cho bạn về các quy chế học vụ?",
      },
    ]);
    setDialogConfig({ type: null });
  };

  // --- Folder CRUD ---
  const openAddFolder = (parentId: string | null = null) => {
    setDialogInputValue("");
    setDialogConfig({ type: "add-folder", data: { parentId } });
  };

  const handleAddFolder = () => {
    if (!dialogInputValue.trim()) return;
    const newFolder: Folder = {
      id: Date.now().toString(),
      name: dialogInputValue,
      parentId: dialogConfig.data?.parentId || null,
    };
    setFolders([...folders, newFolder]);
    setDialogConfig({ type: null });
  };

  const openRenameFolder = (folder: Folder) => {
    setDialogInputValue(folder.name);
    setDialogConfig({ type: "rename-folder", data: folder });
  };

  const handleRenameFolder = () => {
    if (!dialogInputValue.trim()) return;
    setFolders(folders.map((f) => (f.id === dialogConfig.data.id ? { ...f, name: dialogInputValue } : f)));
    setDialogConfig({ type: null });
  };

  const openDeleteFolder = (folder: Folder) => {
    setDialogConfig({ type: "delete-folder", data: folder });
  };

  const handleDeleteFolder = () => {
    const id = dialogConfig.data.id;
    // Recursive delete children
    const getChildrenIds = (parentId: string): string[] => {
      const children = folders.filter((f) => f.parentId === parentId);
      return [parentId, ...children.flatMap((c) => getChildrenIds(c.id))];
    };
    const idsToDelete = getChildrenIds(id);
    setFolders(folders.filter((f) => !idsToDelete.includes(f.id)));
    if (selectedFolderId && idsToDelete.includes(selectedFolderId)) {
      setSelectedFolderId(null);
    }
    setDialogConfig({ type: null });
  };

  // --- Tag CRUD ---
  const openAddTag = () => {
    setDialogInputValue("");
    setDialogConfig({ type: "add-tag" });
  };

  const handleAddTag = () => {
    if (!dialogInputValue.trim()) return;
    const newTag: Tag = {
      id: "t" + Date.now(),
      name: dialogInputValue,
      color: "bg-blue-100 text-blue-700",
    };
    setTags([...tags, newTag]);
    setDialogConfig({ type: null });
  };

  const openEditTag = (tag: Tag) => {
    setDialogInputValue(tag.name);
    setDialogConfig({ type: "edit-tag", data: tag });
  };

  const handleEditTag = () => {
    if (!dialogInputValue.trim()) return;
    setTags(tags.map((t) => (t.id === dialogConfig.data.id ? { ...t, name: dialogInputValue } : t)));
    setDialogConfig({ type: null });
  };

  const openDeleteTag = (tag: Tag) => {
    setDialogConfig({ type: "delete-tag", data: tag });
  };

  const handleDeleteTag = () => {
    setTags(tags.filter((t) => t.id !== dialogConfig.data.id));
    setDialogConfig({ type: null });
  };

  // --- Document CRUD ---
  const openEditDoc = (doc: Document) => {
    setDialogInputValue(doc.name);
    setDialogSelectedFolderId(doc.folderId);
    setDialogSelectedTagIds(doc.tagIds);
    setDialogConfig({ type: "edit-doc", data: doc });
  };

  const handleEditDoc = () => {
    if (!dialogInputValue.trim() || !dialogSelectedFolderId) return;
    setDocuments(
      documents.map((d) =>
        d.id === dialogConfig.data.id
          ? {
              ...d,
              name: dialogInputValue,
              folderId: dialogSelectedFolderId,
              tagIds: dialogSelectedTagIds,
            }
          : d
      )
    );
    setDialogConfig({ type: null });
  };

  const openDeleteDoc = (doc: Document) => {
    setDialogConfig({ type: "delete-doc", data: doc });
  };

  const handleDeleteDoc = () => {
    setDocuments(documents.filter((d) => d.id !== dialogConfig.data.id));
    setDialogConfig({ type: null });
  };

  const openUploadModal = () => {
    setDialogInputValue("");
    setDialogSelectedFolderId(folders[0]?.id || null);
    setDialogSelectedTagIds([]);
    setShowUploadModal(true);
  };

  const uploadDocument = (e: React.FormEvent) => {
    e.preventDefault();
    if (!dialogSelectedFolderId) return;
    // Simple mock upload
    const newDoc: Document = {
      id: Date.now().toString(),
      name: dialogInputValue || "Tài liệu mới tải lên",
      extension: "pdf",
      createdAt: new Date().toISOString().split("T")[0],
      folderId: dialogSelectedFolderId,
      tagIds: dialogSelectedTagIds,
    };
    setDocuments([...documents, newDoc]);
    setShowUploadModal(false);
  };

  const filteredDocs = selectedFolderId ? documents.filter((d) => d.folderId === selectedFolderId) : documents;

  return (
    <div className="flex h-screen bg-white overflow-hidden">
      {/* Sidebar */}
      <aside className="w-80 border-r border-slate-200 flex flex-col bg-slate-50/50">
        <div className="p-4 border-bottom border-slate-200 flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">U</div>
          <h1 className="font-bold text-lg text-slate-800">UniRAG SGU</h1>
        </div>

        {/* Tabs Navigation */}
        <div className="flex px-4 mt-2 gap-1">
          {(["folders", "documents", "tags"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => {
                setActiveTab(tab);
                if (tab !== "folders") setSelectedFolderId(null);
              }}
              className={cn(
                "flex-1 py-2 text-xs font-medium rounded-md transition-all",
                activeTab === tab
                  ? "bg-white shadow-sm text-blue-600 ring-1 ring-slate-200"
                  : "text-slate-500 hover:text-slate-700"
              )}
            >
              {tab === "folders" && "Thư mục"}
              {tab === "documents" && "Tài liệu"}
              {tab === "tags" && "Nhãn"}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === "folders" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Cấu trúc thư mục</h3>
                <button
                  onClick={() => openAddFolder(null)}
                  title="Thêm thư mục gốc"
                  className="p-1 hover:bg-blue-50 text-blue-600 rounded-md transition-colors"
                >
                  <Plus size={16} />
                </button>
              </div>
              <div className="space-y-1">
                {folders
                  .filter((f) => !f.parentId)
                  .map((folder) => (
                    <FolderNode
                      key={folder.id}
                      folder={folder}
                      allFolders={folders}
                      onAdd={openAddFolder}
                      onRename={openRenameFolder}
                      onDelete={openDeleteFolder}
                      onSelect={setSelectedFolderId}
                      selectedId={selectedFolderId}
                    />
                  ))}
              </div>

              {/* Folder Content View */}
              {selectedFolderId && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-6 pt-6 border-t border-slate-200"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-xs font-bold text-slate-800 flex items-center gap-2">
                      <FileText size={14} className="text-blue-600" />
                      Tài liệu trong thư mục
                    </h4>
                    <span className="text-[10px] bg-slate-200 px-1.5 py-0.5 rounded text-slate-600 font-bold">
                      {filteredDocs.length}
                    </span>
                  </div>
                  <div className="space-y-2">
                    {filteredDocs.length > 0 ? (
                      filteredDocs.map((doc) => (
                        <div
                          key={doc.id}
                          className="p-2 bg-white border border-slate-200 rounded-lg text-xs flex items-center gap-2"
                        >
                          <FileText size={14} className="text-slate-400" />
                          <span className="truncate flex-1">{doc.name}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-[10px] text-slate-400 italic text-center py-4">Thư mục trống</p>
                    )}
                  </div>
                </motion.div>
              )}
            </div>
          )}

          {activeTab === "documents" && (
            <div className="space-y-4">
              <button
                onClick={openUploadModal}
                className="w-full flex items-center justify-center gap-2 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors shadow-sm"
              >
                <Upload size={16} />
                Tải tài liệu lên
              </button>

              <div className="space-y-3">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className="p-3 bg-white border border-slate-200 rounded-xl hover:border-blue-300 transition-all group shadow-sm"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex gap-3">
                        <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center text-blue-600 shrink-0">
                          <FileText size={20} />
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-slate-800 truncate">{doc.name}</p>
                          <p className="text-[10px] text-slate-400 uppercase font-bold">
                            {doc.extension} • {doc.createdAt}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => openEditDoc(doc)}
                          className="p-1 text-slate-300 hover:text-blue-600 transition-colors"
                        >
                          <Edit2 size={14} />
                        </button>
                        <button
                          onClick={() => openDeleteDoc(doc)}
                          className="p-1 text-slate-300 hover:text-red-500 transition-colors"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {doc.tagIds.map((tid) => {
                        const tag = tags.find((t) => t.id === tid);
                        return tag ? (
                          <span
                            key={tid}
                            className={cn("text-[10px] px-1.5 py-0.5 rounded-full font-medium", tag.color)}
                          >
                            {tag.name}
                          </span>
                        ) : null;
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "tags" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Quản lý nhãn</h3>
                <button onClick={openAddTag} className="p-1 hover:bg-blue-50 text-blue-600 rounded-md">
                  <Plus size={16} />
                </button>
              </div>
              <div className="grid grid-cols-1 gap-2">
                {tags.map((tag) => (
                  <div
                    key={tag.id}
                    className="flex items-center justify-between p-2 bg-white border border-slate-200 rounded-lg"
                  >
                    <div className="flex items-center gap-2">
                      <div className={cn("w-3 h-3 rounded-full", tag.color.split(" ")[0])} />
                      <span className="text-sm font-medium text-slate-700">{tag.name}</span>
                    </div>
                    <div className="flex gap-1">
                      <button onClick={() => openEditTag(tag)} className="p-1 text-slate-400 hover:text-slate-600">
                        <Edit2 size={14} />
                      </button>
                      <button onClick={() => openDeleteTag(tag)} className="p-1 text-slate-400 hover:text-red-500">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar Footer Removed */}
      </aside>

      {/* Main Area - Chat */}
      <main className="flex-1 flex flex-col relative bg-white">
        {/* Chat Header */}
        <header className="h-16 border-b border-slate-200 flex items-center justify-between px-6 bg-white/80 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-3">
            <MessageSquare className="text-blue-600" size={20} />
            <h2 className="font-bold text-slate-800">Tư vấn học vụ AI</h2>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setDialogConfig({ type: "clear-chat" })}
              className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 rounded-lg transition-all border border-transparent hover:border-red-100"
              title="Xóa cuộc trò chuyện"
            >
              <RotateCcw size={16} />
              <span className="hidden md:inline">Làm mới chat</span>
            </button>
            <div className="flex items-center gap-1 text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              AI Online
            </div>
          </div>
        </header>

        {/* Messages List */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-8 scroll-smooth">
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
            {/* Context Filters Popover */}
            <AnimatePresence>
              {showFilters && (
                <motion.div
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 10, scale: 0.95 }}
                  className="absolute bottom-full mb-4 w-full bg-white border border-slate-200 rounded-2xl shadow-xl p-4 z-20"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                      <Filter size={16} className="text-blue-600" />
                      Bộ lọc ngữ cảnh
                    </h4>
                    <button onClick={() => setShowFilters(false)} className="text-slate-400 hover:text-slate-600">
                      <X size={18} />
                    </button>
                  </div>

                  <div className="grid grid-cols-3 gap-6">
                    <div className="space-y-3">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                        <FileText size={12} />
                        Tài liệu
                      </p>
                      <div className="h-48 overflow-y-auto space-y-1 pr-2 border-r border-slate-100">
                        {documents.map((d) => (
                          <label
                            key={d.id}
                            className="flex items-center gap-2 p-2 hover:bg-slate-50 rounded-lg cursor-pointer transition-colors group"
                          >
                            <input
                              type="checkbox"
                              className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500/20 transition-all"
                              checked={filters.docIds.includes(d.id)}
                              onChange={(e) => {
                                const newIds = e.target.checked
                                  ? [...filters.docIds, d.id]
                                  : filters.docIds.filter((id) => id !== d.id);
                                setFilters({ ...filters, docIds: newIds });
                              }}
                            />
                            <span className="text-xs text-slate-600 truncate group-hover:text-blue-600">{d.name}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                    <div className="space-y-3">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                        <FolderIcon size={12} />
                        Thư mục
                      </p>
                      <div className="h-48 overflow-y-auto space-y-1 pr-2 border-r border-slate-100">
                        {folders.map((f) => (
                          <label
                            key={f.id}
                            className="flex items-center gap-2 p-2 hover:bg-slate-50 rounded-lg cursor-pointer transition-colors group"
                          >
                            <input
                              type="checkbox"
                              className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500/20 transition-all"
                              checked={filters.folderIds.includes(f.id)}
                              onChange={(e) => {
                                const newIds = e.target.checked
                                  ? [...filters.folderIds, f.id]
                                  : filters.folderIds.filter((id) => id !== f.id);
                                setFilters({ ...filters, folderIds: newIds });
                              }}
                            />
                            <span className="text-xs text-slate-600 truncate group-hover:text-blue-600">{f.name}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                    <div className="space-y-3">
                      <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                        <TagIcon size={12} />
                        Nhãn
                      </p>
                      <div className="h-48 overflow-y-auto space-y-1 pr-2">
                        {tags.map((t) => (
                          <label
                            key={t.id}
                            className="flex items-center gap-2 p-2 hover:bg-slate-50 rounded-lg cursor-pointer transition-colors group"
                          >
                            <input
                              type="checkbox"
                              className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500/20 transition-all"
                              checked={filters.tagIds.includes(t.id)}
                              onChange={(e) => {
                                const newIds = e.target.checked
                                  ? [...filters.tagIds, t.id]
                                  : filters.tagIds.filter((id) => id !== t.id);
                                setFilters({ ...filters, tagIds: newIds });
                              }}
                            />
                            <span className="text-xs text-slate-600 truncate group-hover:text-blue-600">{t.name}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="relative group">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="Nhập câu hỏi về học vụ SGU..."
                className="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-4 pr-32 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all resize-none min-h-[60px] max-h-48 text-sm"
                rows={1}
              />

              <div className="absolute right-2 bottom-2 flex items-center gap-2">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={cn(
                    "p-2 rounded-xl transition-all flex items-center gap-1.5 text-xs font-medium",
                    showFilters ? "bg-blue-100 text-blue-600" : "text-slate-400 hover:text-slate-600 hover:bg-slate-200"
                  )}
                >
                  <Filter size={18} />
                  <span className="hidden sm:inline">Lọc</span>
                </button>

                {isStreaming ? (
                  <button
                    onClick={handleStopStreaming}
                    className="p-2 bg-red-100 text-red-600 rounded-xl hover:bg-red-200 transition-all"
                  >
                    <Square size={18} fill="currentColor" />
                  </button>
                ) : (
                  <button
                    onClick={handleSendMessage}
                    disabled={!input.trim()}
                    className="p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-blue-200"
                  >
                    <Send size={18} />
                  </button>
                )}
              </div>
            </div>
            <p className="text-[10px] text-center text-slate-400 mt-3 font-medium">
              UniRAG có thể đưa ra thông tin chưa chính xác. Vui lòng kiểm tra lại với phòng Đào tạo.
            </p>
          </div>
        </div>
      </main>

      {/* Dialogs */}
      <Dialog
        isOpen={!!dialogConfig.type}
        onClose={() => setDialogConfig({ type: null })}
        title={
          dialogConfig.type === "delete-folder"
            ? "Xác nhận xóa thư mục"
            : dialogConfig.type === "delete-tag"
              ? "Xác nhận xóa nhãn"
              : dialogConfig.type === "delete-doc"
                ? "Xác nhận xóa tài liệu"
                : dialogConfig.type === "clear-chat"
                  ? "Làm mới cuộc trò chuyện"
                  : dialogConfig.type === "rename-folder"
                    ? "Đổi tên thư mục"
                    : dialogConfig.type === "add-folder"
                      ? "Thêm thư mục mới"
                      : dialogConfig.type === "add-tag"
                        ? "Thêm nhãn mới"
                        : dialogConfig.type === "edit-tag"
                          ? "Chỉnh sửa nhãn"
                          : dialogConfig.type === "edit-doc"
                            ? "Chỉnh sửa tài liệu"
                            : ""
        }
        description={
          dialogConfig.type === "clear-chat"
            ? "Bạn có chắc chắn muốn xóa toàn bộ nội dung cuộc trò chuyện này không? Nội dung sau khi xóa sẽ không thể khôi phục."
            : dialogConfig.type?.startsWith("delete")
              ? `Hành động này không thể hoàn tác. Bạn có chắc chắn muốn xóa "${dialogConfig.data?.name}"?`
              : undefined
        }
        footer={
          <>
            <button
              onClick={() => setDialogConfig({ type: null })}
              className="px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition-all"
            >
              Hủy
            </button>
            <button
              onClick={() => {
                if (dialogConfig.type === "delete-folder") handleDeleteFolder();
                if (dialogConfig.type === "delete-tag") handleDeleteTag();
                if (dialogConfig.type === "delete-doc") handleDeleteDoc();
                if (dialogConfig.type === "clear-chat") handleClearChat();
                if (dialogConfig.type === "rename-folder") handleRenameFolder();
                if (dialogConfig.type === "add-folder") handleAddFolder();
                if (dialogConfig.type === "add-tag") handleAddTag();
                if (dialogConfig.type === "edit-tag") handleEditTag();
                if (dialogConfig.type === "edit-doc") handleEditDoc();
              }}
              className={cn(
                "px-4 py-2 text-sm font-semibold text-white rounded-xl transition-all shadow-md",
                dialogConfig.type?.startsWith("delete") || dialogConfig.type === "clear-chat"
                  ? "bg-red-600 hover:bg-red-700 shadow-red-100"
                  : "bg-blue-600 hover:bg-blue-700 shadow-blue-100"
              )}
            >
              Xác nhận
            </button>
          </>
        }
      >
        {dialogConfig.type === "edit-doc" && (
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tên tài liệu</label>
              <input
                autoFocus
                type="text"
                value={dialogInputValue}
                onChange={(e) => setDialogInputValue(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Gán nhãn (Chọn nhiều)</label>
              <div className="flex flex-wrap gap-2 p-3 bg-slate-50 border border-slate-200 rounded-xl min-h-[44px]">
                {tags.map((tag) => (
                  <button
                    key={tag.id}
                    type="button"
                    onClick={() => {
                      const newIds = dialogSelectedTagIds.includes(tag.id)
                        ? dialogSelectedTagIds.filter((id) => id !== tag.id)
                        : [...dialogSelectedTagIds, tag.id];
                      setDialogSelectedTagIds(newIds);
                    }}
                    className={cn(
                      "text-[10px] px-2 py-1 rounded-full font-bold transition-all border",
                      dialogSelectedTagIds.includes(tag.id)
                        ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                        : "bg-white text-slate-500 border-slate-200 hover:border-blue-300"
                    )}
                  >
                    {tag.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Thư mục lưu trữ (Tree View)
              </label>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl max-h-48 overflow-y-auto">
                {folders
                  .filter((f) => !f.parentId)
                  .map((folder) => (
                    <TreeSelectNode
                      key={folder.id}
                      folder={folder}
                      allFolders={folders}
                      selectedId={dialogSelectedFolderId}
                      onSelect={setDialogSelectedFolderId}
                    />
                  ))}
              </div>
            </div>
          </div>
        )}

        {(dialogConfig.type === "rename-folder" ||
          dialogConfig.type === "add-folder" ||
          dialogConfig.type === "add-tag" ||
          dialogConfig.type === "edit-tag") && (
          <input
            autoFocus
            type="text"
            value={dialogInputValue}
            onChange={(e) => setDialogInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                if (dialogConfig.type === "rename-folder") handleRenameFolder();
                if (dialogConfig.type === "add-folder") handleAddFolder();
                if (dialogConfig.type === "add-tag") handleAddTag();
                if (dialogConfig.type === "edit-tag") handleEditTag();
              }
            }}
            placeholder="Nhập tên..."
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
          />
        )}
      </Dialog>

      {/* Upload Modal */}
      <AnimatePresence>
        {showUploadModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowUploadModal(false)}
              className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-lg bg-white rounded-3xl shadow-2xl overflow-hidden"
            >
              <div className="p-6 border-b border-slate-100">
                <h3 className="text-xl font-bold text-slate-800">Tải tài liệu mới</h3>
                <p className="text-sm text-slate-500">Thêm tri thức vào hệ thống RAG</p>
              </div>

              <form onSubmit={uploadDocument} className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tên tài liệu</label>
                  <input
                    type="text"
                    value={dialogInputValue}
                    onChange={(e) => setDialogInputValue(e.target.value)}
                    placeholder="Nhập tên tài liệu (tùy chọn)..."
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Chọn tệp tin</label>
                  <div className="border-2 border-dashed border-slate-200 rounded-2xl p-6 flex flex-col items-center justify-center gap-3 hover:border-blue-400 hover:bg-blue-50 transition-all cursor-pointer group">
                    <div className="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center text-blue-600 group-hover:scale-110 transition-transform">
                      <Upload size={20} />
                    </div>
                    <div className="text-center">
                      <p className="text-xs font-semibold text-slate-700">Kéo thả hoặc Click để chọn</p>
                      <p className="text-[10px] text-slate-400 uppercase font-bold">PDF, DOCX, TXT</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Gán nhãn</label>
                  <div className="flex flex-wrap gap-2 p-3 bg-slate-50 border border-slate-200 rounded-xl">
                    {tags.map((tag) => (
                      <button
                        key={tag.id}
                        type="button"
                        onClick={() => {
                          const newIds = dialogSelectedTagIds.includes(tag.id)
                            ? dialogSelectedTagIds.filter((id) => id !== tag.id)
                            : [...dialogSelectedTagIds, tag.id];
                          setDialogSelectedTagIds(newIds);
                        }}
                        className={cn(
                          "text-[10px] px-2 py-1 rounded-full font-bold transition-all border",
                          dialogSelectedTagIds.includes(tag.id)
                            ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                            : "bg-white text-slate-500 border-slate-200 hover:border-blue-300"
                        )}
                      >
                        {tag.name}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    Thư mục đích (Tree View)
                  </label>
                  <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl max-h-48 overflow-y-auto">
                    {folders
                      .filter((f) => !f.parentId)
                      .map((folder) => (
                        <TreeSelectNode
                          key={folder.id}
                          folder={folder}
                          allFolders={folders}
                          selectedId={dialogSelectedFolderId}
                          onSelect={setDialogSelectedFolderId}
                        />
                      ))}
                  </div>
                </div>

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowUploadModal(false)}
                    className="flex-1 py-2.5 border border-slate-200 text-slate-600 rounded-xl font-semibold hover:bg-slate-50 transition-all"
                  >
                    Hủy
                  </button>
                  <button
                    type="submit"
                    className="flex-1 py-2.5 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-all shadow-lg shadow-blue-200"
                  >
                    Tải lên ngay
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
