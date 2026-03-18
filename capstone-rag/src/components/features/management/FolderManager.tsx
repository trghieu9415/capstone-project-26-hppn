import React, { useEffect, useState } from "react";
import { Folder, Plus, ChevronRight, ChevronDown, Trash2, Edit2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useFolderStore } from "@/stores/useFolderStore";
import { useUIStore } from "@/stores/useUIStore";
import { FolderDTO } from "@/types/folder";

interface FolderNodeProps {
  folder: FolderDTO;
  level?: number;
}

const FolderNode: React.FC<FolderNodeProps> = ({ folder, level = 0 }) => {
  const [isOpen, setIsOpen] = useState(true);

  const { folders } = useFolderStore();
  const { selectedFolderId, setSelectedFolderId, openDialog } = useUIStore();

  const children = folders.filter((f) => f.parentId === folder.id);
  const hasChildren = children.length > 0;
  const isSelected = selectedFolderId === folder.id;

  return (
    <div className="select-none">
      <div
        onClick={() => setSelectedFolderId(folder.id)}
        className={cn(
          "flex items-center group py-1.5 px-2 rounded-lg cursor-pointer transition-all",
          isSelected ? "bg-blue-100 text-blue-700 shadow-sm" : "hover:bg-slate-100 text-slate-600",
          level > 0 && "ml-4"
        )}
      >
        <div
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(!isOpen);
          }}
          className="p-1 hover:bg-black/5 rounded"
        >
          {hasChildren ? isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} /> : <div className="w-3.5" />}
        </div>
        <Folder size={16} className={cn("mr-2 shrink-0", isSelected ? "text-blue-600" : "text-blue-400")} />
        <span className="text-sm flex-1 truncate font-medium">{folder.name}</span>

        <div className="hidden group-hover:flex items-center gap-1 ml-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              openDialog("add-folder", { parentId: folder.id });
            }}
            title="Thêm thư mục con"
            className="p-1 hover:bg-blue-200 rounded text-blue-600"
          >
            <Plus size={14} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              openDialog("rename-folder", folder);
            }}
            title="Đổi tên"
            className="p-1 hover:bg-slate-200 rounded text-slate-500"
          >
            <Edit2 size={14} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              openDialog("delete-folder", folder);
            }}
            title="Xóa"
            className="p-1 hover:bg-red-100 rounded text-red-500"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {isOpen && hasChildren && (
        <div className="border-l border-slate-200 ml-3.5 mt-1 pl-1">
          {children.map((child) => (
            <FolderNode key={child.id} folder={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export const FolderManager: React.FC = () => {
  const { folders, fetchFolders } = useFolderStore();
  const { openDialog } = useUIStore();
  const rootFolders = folders.filter((f) => !f.parentId);

  useEffect(() => {
    fetchFolders();
  }, [fetchFolders]);

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between mb-4 px-2">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Thư mục</h3>
        <button
          onClick={() => openDialog("add-folder", { parentId: null })}
          className="p-1 hover:bg-blue-50 text-blue-600 rounded-lg transition-colors"
          title="Thêm thư mục gốc"
        >
          <Plus size={16} />
        </button>
      </div>

      {rootFolders.length > 0 ? (
        rootFolders.map((folder) => <FolderNode key={folder.id} folder={folder} />)
      ) : (
        <div className="text-center py-8 px-4 border-2 border-dashed border-slate-100 rounded-2xl">
          <Folder size={24} className="mx-auto text-slate-200 mb-2" />
          <p className="text-xs text-slate-400">Chưa có thư mục nào</p>
        </div>
      )}
    </div>
  );
};
