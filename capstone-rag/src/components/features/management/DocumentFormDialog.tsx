import React, { useEffect, useState } from "react";
import { Dialog } from "../../shared/Dialog";
import { TreeSelectNode } from "../../shared/TreeSelectNode";
import { SystemNodeDTO } from "@/types/folder";
import { DocumentDTO } from "@/types/document";
import { TagDTO } from "@/types/tag";

interface DocumentFormDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (id: string, name: string, folderId: string, tagIds: string[]) => void;
  document: DocumentDTO;
  folders: SystemNodeDTO[];
  tags: TagDTO[];
}

export const DocumentFormDialog: React.FC<DocumentFormDialogProps> = ({
  isOpen,
  onClose,
  onSave,
  document,
  folders,
  tags,
}) => {
  const [name, setName] = useState(document.name);
  const [folderId, setFolderId] = useState(document.folder.id);
  const [tagIds, setTagIds] = useState<string[]>(document.tags.map((t) => t.id));

  useEffect(() => {
    if (isOpen) {
      setName(document.name);
      setFolderId(document.folder.id);
      setTagIds(document.tags.map((t) => t.id));
    }
  }, [isOpen, document]);

  const rootFolders = folders.filter((f) => !f.parentId && f.type !== "DOCUMENT");

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title="Chỉnh sửa tài liệu"
      footer={
        <>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
          >
            Hủy
          </button>
          <button
            onClick={() => onSave(document.id, name, folderId, tagIds)}
            disabled={!name.trim()}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all shadow-sm shadow-blue-200"
          >
            Lưu thay đổi
          </button>
        </>
      }
    >
      <div className="space-y-6">
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tên tài liệu</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Thư mục</label>
          <div className="border border-slate-100 rounded-2xl p-2 max-h-48 overflow-y-auto bg-slate-50/30 custom-scrollbar">
            {rootFolders.map((folder) => (
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

        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Nhãn</label>
          <div className="flex flex-wrap gap-2">
            {tags.map((tag) => (
              <button
                key={tag.id}
                onClick={() => {
                  setTagIds((prev) => (prev.includes(tag.id) ? prev.filter((id) => id !== tag.id) : [...prev, tag.id]));
                }}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold uppercase tracking-wider transition-all border-2 ${
                  tagIds.includes(tag.id)
                    ? "bg-blue-600 border-blue-600 text-white shadow-md shadow-blue-100"
                    : "bg-white border-slate-100 text-slate-400 hover:border-slate-200"
                }`}
              >
                {tag.name}
              </button>
            ))}
          </div>
        </div>
      </div>
    </Dialog>
  );
};
