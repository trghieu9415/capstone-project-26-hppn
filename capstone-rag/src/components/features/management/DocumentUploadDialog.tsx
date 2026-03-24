import React, { useEffect, useState, useRef } from "react";
import { Upload, FileText, X, Loader2 } from "lucide-react";
import { Dialog } from "../../shared/Dialog";
import { TreeSelectNode } from "../../shared/TreeSelectNode";
import { cn } from "@/lib/utils";
import { SystemNodeDTO } from "@/types/folder";
import { TagDTO } from "@/types/tag";

interface DocumentUploadDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (file: File, folderId: string) => void;
  folders: SystemNodeDTO[];
  tags: TagDTO[];
  isUploading?: boolean;
}

export const DocumentUploadDialog: React.FC<DocumentUploadDialogProps> = ({
  isOpen,
  onClose,
  onUpload,
  folders,
  tags,
  isUploading = false,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [folderId, setFolderId] = useState<string | null>(null);
  const [tagIds, setTagIds] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setSelectedFile(null);

      const rootFolders = folders.filter((f) => !f.parentId && f.type !== "DOCUMENT");
      setFolderId(rootFolders[0]?.id || null);
      setTagIds([]);
    }
  }, [isOpen, folders]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUploadClick = () => {
    if (selectedFile && folderId) {
      onUpload(selectedFile, folderId);
    }
  };

  const handleClose = () => {
    if (!isUploading) onClose();
  };

  return (
    <Dialog
      isOpen={isOpen}
      onClose={handleClose}
      title="Tải tài liệu mới"
      description="Thêm tri thức vào hệ thống RAG"
      footer={
        <>
          <button
            onClick={handleClose}
            disabled={isUploading}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-colors"
          >
            Hủy
          </button>
          <button
            onClick={handleUploadClick}
            disabled={!folderId || !selectedFile || isUploading}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all shadow-sm shadow-blue-200"
          >
            {isUploading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Đang xử lý...
              </>
            ) : (
              "Tải lên ngay"
            )}
          </button>
        </>
      }
    >
      <div className="space-y-6">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.docx,.txt"
          className="hidden"
          disabled={isUploading}
        />

        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Chọn tệp tin</label>

          {!selectedFile ? (
            <div
              onClick={() => !isUploading && fileInputRef.current?.click()}
              className={cn(
                "border-2 border-dashed border-slate-200 rounded-2xl p-8 flex flex-col items-center justify-center gap-3 transition-all",
                isUploading
                  ? "opacity-50 cursor-not-allowed bg-slate-50"
                  : "hover:border-blue-400 hover:bg-blue-50 cursor-pointer group"
              )}
            >
              <div
                className={cn(
                  "w-12 h-12 bg-blue-50 rounded-full flex items-center justify-center text-blue-600 transition-transform",
                  !isUploading && "group-hover:scale-110"
                )}
              >
                <Upload size={24} />
              </div>
              <div className="text-center">
                <p className="text-sm font-semibold text-slate-700">Click để chọn tài liệu</p>
                <p className="text-[10px] text-slate-400 uppercase font-bold mt-1">PDF, DOCX, TXT tối đa 20MB</p>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between p-4 bg-blue-50 border border-blue-100 rounded-2xl">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white rounded-lg text-blue-600 shadow-sm">
                  <FileText size={20} />
                </div>
                <div>
                  <p className="text-sm font-medium text-slate-700 truncate max-w-50">{selectedFile.name}</p>
                  <p className="text-[10px] text-slate-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedFile(null)}
                disabled={isUploading}
                className="p-1 hover:bg-blue-100 disabled:opacity-50 disabled:hover:bg-transparent rounded-full text-slate-400 hover:text-red-500 transition-colors"
              >
                <X size={18} />
              </button>
            </div>
          )}
        </div>

        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Gán nhãn</label>
          <div
            className={cn(
              "flex flex-wrap gap-2 p-3 bg-slate-50 border border-slate-200 rounded-xl",
              isUploading && "opacity-60 pointer-events-none"
            )}
          >
            {tags.map((tag) => (
              <button
                key={tag.id}
                type="button"
                onClick={() => {
                  setTagIds((prev) => (prev.includes(tag.id) ? prev.filter((id) => id !== tag.id) : [...prev, tag.id]));
                }}
                className={cn(
                  "text-[10px] px-2 py-1 rounded-full font-bold transition-all border",
                  tagIds.includes(tag.id)
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
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Thư mục đích</label>
          <div
            className={cn(
              "p-1 bg-slate-50 border border-slate-200 rounded-xl max-h-40 overflow-y-auto custom-scrollbar",
              isUploading && "opacity-60 pointer-events-none"
            )}
          >
            {folders
              .filter((f) => !f.parentId && f.type !== "DOCUMENT")
              .map((folder) => (
                <TreeSelectNode
                  key={folder.id}
                  folder={folder}
                  allFolders={folders}
                  selectedId={folderId}
                  onSelect={setFolderId}
                />
              ))}
          </div>
        </div>
      </div>
    </Dialog>
  );
};
