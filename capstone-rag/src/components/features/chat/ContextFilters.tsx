import React from "react";
import { FileText, Folder, Tag, X } from "lucide-react";
import { motion } from "motion/react";
import { useDocumentStore } from "@/stores/useDocumentStore";
import { useFolderStore } from "@/stores/useFolderStore";
import { useUIStore } from "@/stores/useUIStore";
import { useTagStore } from "@/stores/useTagStore";

export const ContextFilters: React.FC = () => {
  const { setShowFilters } = useUIStore();
  const { filters, setFilters, documents } = useDocumentStore();
  const { folders } = useFolderStore();
  const { tags } = useTagStore();

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 10, scale: 0.95 }}
      className="absolute bottom-full left-0 right-0 mb-4 bg-white rounded-3xl shadow-2xl border border-slate-100 p-6 z-50"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
          Phạm vi tìm kiếm
        </h3>
        <button
          onClick={() => setShowFilters(false)}
          className="p-1.5 hover:bg-slate-100 rounded-xl text-slate-400 transition-colors"
        >
          <X size={18} />
        </button>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="space-y-3">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
            <FileText size={12} />
            Tài liệu
          </p>
          <div className="h-48 overflow-y-auto space-y-1 pr-2 border-r border-slate-100 custom-scrollbar">
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
            <Folder size={12} />
            Thư mục
          </p>
          <div className="h-48 overflow-y-auto space-y-1 pr-2 border-r border-slate-100 custom-scrollbar">
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
            <Tag size={12} />
            Nhãn
          </p>
          <div className="h-48 overflow-y-auto space-y-1 pr-2 custom-scrollbar">
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
  );
};
