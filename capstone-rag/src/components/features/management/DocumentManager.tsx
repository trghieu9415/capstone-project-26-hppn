import React, { useEffect } from "react";
import { FileText, Trash2, Edit2, Search, Upload, Folder as FolderIcon } from "lucide-react";
import { useFolderStore } from "@/stores/useFolderStore";
import { useTagStore } from "@/stores/useTagStore";
import { useUIStore } from "@/stores/useUIStore";
import { TagDTO } from "@/types/tag";
import { cn } from "@/lib/utils";
import { useDocumentStore } from "@/stores/useDocumentStore";

export const DocumentManager: React.FC = () => {
  const { folders, fetchFolders } = useFolderStore();
  const { tags, fetchTags } = useTagStore();
	const { fetchDocuments } = useDocumentStore();
  const { openDialog } = useUIStore();

  useEffect(() => {
    fetchFolders();
    fetchTags();
		fetchDocuments();
  }, [fetchDocuments, fetchFolders, fetchTags]);

  // Chỉ lấy những phần tử là tài liệu
  const documents = folders.filter((f) => f.type === "DOCUMENT");

  // Lấy tên thư mục chứa
  const getFolderName = (parentId?: string | null) => {
    if (!parentId) return "Thư mục gốc";
    const folder = folders.find((f) => f.id === parentId);
    return folder ? folder.name : "Thư mục không xác định";
  };

  // Lấy chi tiết Tag (để lấy màu sắc)
  const getDocumentTags = (tagIds?: string[]): TagDTO[] => {
    if (!tagIds) return [];
    const result: TagDTO[] = [];
    tagIds.forEach((id) => {
      const t = tags.find((tag) => tag.id === id);
      if (t) result.push(t);
    });
    return result;
  };

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex items-center justify-between px-2 shrink-0">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tài liệu</h3>
        <button
          onClick={() => openDialog("upload-doc")}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl transition-all shadow-sm shadow-blue-200"
        >
          <Upload size={14} />
          Tải lên
        </button>
      </div>

      <div className="relative px-2 shrink-0">
        <Search size={14} className="absolute left-5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          placeholder="Tìm kiếm tài liệu..."
          className="w-full bg-slate-100 border-none rounded-xl py-2 pl-9 pr-4 text-xs focus:ring-2 focus:ring-blue-500/20 transition-all"
        />
      </div>

      <div className="space-y-2 px-1 flex-1 overflow-y-auto custom-scrollbar min-h-0 pb-4">
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

                  {/* Thư mục */}
                  <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400 font-medium uppercase tracking-wider">
                    <span>•</span>
                    <span className="flex items-center gap-1 text-slate-500">
                      <FolderIcon size={10} />
                      <span className="truncate max-w-30">{getFolderName(doc.parentId)}</span>
                    </span>
                  </div>
                </div>
                <div className="flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() =>
                      // Fake payload để Dialog xử lý khớp dữ liệu
                      openDialog("edit-doc", {
                        id: doc.id,
                        name: doc.name,
                        folder: { id: doc.parentId || undefined },
                        tags: doc.tagIds?.map((id) => ({ id })) || [],
                      })
                    }
                    className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-blue-600 transition-colors"
                  >
                    <Edit2 size={14} />
                  </button>
                  <button
                    onClick={() => openDialog("delete-doc", { id: doc.id, name: doc.name })}
                    className="p-1.5 hover:bg-red-50 rounded-lg text-slate-400 hover:text-red-600 transition-colors"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
              {/* Tags */}
              <div className="flex flex-wrap gap-1 mt-2">
                {getDocumentTags(doc.tagIds).map((tag) => (
                  <span
                    key={tag.id}
                    className={cn(
                      "text-[9px] px-2 py-0.5 rounded-full font-bold uppercase tracking-tight",
                      tag.color // Render màu sắc từ DB (ví dụ: bg-blue-100 text-blue-700)
                    )}
                  >
                    {tag.name}
                  </span>
                ))}
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
