import React, { useEffect, useState } from "react";
import { Dialog } from "../../shared/Dialog";
import { TreeSelectNode } from "../../shared/TreeSelectNode";
import { SystemNodeDTO } from "@/types/folder";

interface FolderDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string, parentId: string | null) => void;
  title: string;
  initialName?: string;
  initialParentId?: string | null;
  folders: SystemNodeDTO[];
  currentFolderId?: string;
}

export const FolderDialog: React.FC<FolderDialogProps> = ({
  isOpen,
  onClose,
  onSave,
  title,
  initialName = "",
  initialParentId = null,
  folders,
  currentFolderId,
}) => {
  const [name, setName] = useState(initialName);
  const [parentId, setParentId] = useState<string | null>(initialParentId);

  useEffect(() => {
    if (isOpen) {
      setName(initialName);
      setParentId(initialParentId);
    }
  }, [isOpen, initialName, initialParentId]);

  const rootFolders = folders.filter((f) => !f.parentId && f.id !== currentFolderId && f.type !== "DOCUMENT");

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      footer={
        <>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
          >
            Hủy
          </button>
          <button
            onClick={() => onSave(name, parentId)}
            disabled={!name.trim()}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all shadow-sm shadow-blue-200"
          >
            Lưu
          </button>
        </>
      }
    >
      <div className="space-y-6">
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tên thư mục</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Nhập tên thư mục..."
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            autoFocus
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Thư mục cha</label>
          <div className="border border-slate-100 rounded-2xl p-2 max-h-48 overflow-y-auto bg-slate-50/30 custom-scrollbar">
            <div
              onClick={() => setParentId(null)}
              className={`flex items-center py-2 px-3 rounded-xl cursor-pointer transition-all mb-1 ${
                parentId === null ? "bg-blue-600 text-white shadow-md" : "hover:bg-slate-100 text-slate-600"
              }`}
            >
              <span className="text-sm font-medium">Gốc (Không có cha)</span>
            </div>
            {rootFolders.map((folder) => (
              <TreeSelectNode
                key={folder.id}
                folder={folder}
                allFolders={folders.filter((f) => f.id !== currentFolderId)}
                selectedId={parentId}
                onSelect={setParentId}
              />
            ))}
          </div>
        </div>
      </div>
    </Dialog>
  );
};
