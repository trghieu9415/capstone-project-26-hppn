import React from "react";
import { FileText, Trash2, Edit2, Search, Upload } from "lucide-react";
import { cn } from "@/lib/utils";
import { useDocumentStore } from "@/stores/useDocumentStore";
import { useTagStore } from "@/stores/useTagStore";
import { useUIStore } from "@/stores/useUIStore";

export const DocumentManager: React.FC = () => {
  const { documents } = useDocumentStore();
  const { tags } = useTagStore();
  const { openDialog } = useUIStore();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between px-2">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tài liệu</h3>
        <button
          onClick={() => openDialog("upload-doc")}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl transition-all shadow-sm shadow-blue-200"
        >
          <Upload size={14} />
          Tải lên
        </button>
      </div>

      <div className="relative px-2">
        <Search size={14} className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="Tìm kiếm tài liệu..."
          className="w-full bg-slate-100 border-none rounded-xl py-2 pl-9 pr-4 text-xs focus:ring-2 focus:ring-blue-500/20 transition-all"
        />
      </div>

      <div className="space-y-2 px-1">
        {documents.length > 0 ? (
          documents.map((doc) => (
            <div
              key={doc.id}
              className="group p-3 hover:bg-white hover:shadow-md hover:shadow-slate-200/50 rounded-2xl transition-all border border-transparent hover:border-slate-100"
            >
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center shrink-0 group-hover:bg-blue-50 transition-colors">
                  <FileText size={20} className="text-slate-400 group-hover:text-blue-500 transition-colors" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-semibold text-slate-700 truncate group-hover:text-blue-700 transition-colors">
                    {doc.name}
                  </h4>
                  <p className="text-[10px] text-slate-400 mt-0.5 font-medium uppercase tracking-wider">
                    {doc.extension} • {doc.createdAt}
                  </p>

                  <div className="flex flex-wrap gap-1 mt-2">
                    {doc.tags.map((tagId) => {
                      const tag = tags.find((t) => t.id === tagId);
                      if (!tag) return null;
                      return (
                        <span
                          key={tag.id}
                          className={cn("text-[9px] px-2 py-0.5 rounded-full font-bold uppercase tracking-tight")}
                        >
                          {tag.name}
                        </span>
                      );
                    })}
                  </div>
                </div>
                <div className="flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => openDialog("edit-doc", doc)}
                    className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-blue-600 transition-colors"
                  >
                    <Edit2 size={14} />
                  </button>
                  <button
                    onClick={() => openDialog("delete-doc", doc)}
                    className="p-1.5 hover:bg-red-50 rounded-lg text-slate-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12 px-4">
            <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4">
              <FileText size={32} className="text-slate-200" />
            </div>
            <p className="text-sm font-medium text-slate-400">Không tìm thấy tài liệu</p>
            <p className="text-xs text-slate-300 mt-1">Hãy thử tải lên tài liệu mới</p>
          </div>
        )}
      </div>
    </div>
  );
};
