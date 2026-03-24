import React, { useEffect, useState } from "react";
import { Folder, FileText, Plus, ChevronRight, ChevronDown, Trash2, Edit2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useFolderStore } from "@/stores/useFolderStore";
import { useUIStore } from "@/stores/useUIStore";
import { SystemNodeDTO } from "@/types/folder";

interface FolderNodeProps {
  folder: SystemNodeDTO;
  level?: number;
}

const FolderNode: React.FC<FolderNodeProps> = ({ folder, level = 0 }) => {
  const [isOpen, setIsOpen] = useState(false);

  const { folders } = useFolderStore();
  const { selectedFolderId, setSelectedFolderId, openDialog } = useUIStore();

  const children = folders.filter((f) => f.parentId === folder.id);
  const hasChildren = children.length > 0;
  const isSelected = selectedFolderId === folder.id;

  // Xác định node là FOLDER hay DOCUMENT
  const isFolder = folder.type !== "DOCUMENT";

  return (
    <div className="select-none">
      <div
        onClick={() => {
          if (isFolder) {
            setSelectedFolderId(folder.id!);
            setIsOpen(!isOpen);
          }
        }}
        className={cn(
          "flex items-center group py-1.5 px-2 rounded-lg cursor-pointer transition-all h-8",
          isFolder && isSelected ? "bg-blue-100 text-blue-700 shadow-sm" : "hover:bg-slate-100 text-slate-600",
          !isFolder && "hover:bg-slate-50",
          level > 0 && "ml-4"
        )}
      >
        <div className={cn("p-1 rounded", isFolder && "hover:bg-black/5")}>
          {isFolder ? (
            hasChildren ? (
              isOpen ? (
                <ChevronDown size={14} />
              ) : (
                <ChevronRight size={14} />
              )
            ) : (
              <div className="w-3.5" />
            )
          ) : (
            <div className="w-3.5" />
          )}
        </div>

        {isFolder ? (
          <Folder size={16} className={cn("mr-2 shrink-0", isSelected ? "text-blue-600" : "text-blue-400")} />
        ) : (
          <FileText size={16} className="mr-2 shrink-0 text-slate-400" />
        )}

        <span className="text-sm flex-1 truncate font-medium">{folder.name}</span>

        <div className="hidden group-hover:flex items-center gap-1 ml-2">
          {isFolder && (
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
          )}
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (isFolder) {
                openDialog("rename-folder", folder);
              } else {
                // Fake format DocumentDTO để Dialog chỉnh sửa tài liệu nhận diện được
                openDialog("edit-doc", {
                  id: folder.id,
                  name: folder.name,
                  folder: { id: folder.parentId || undefined },
                  tags: folder.tagIds?.map((id) => ({ id })) || [],
                });
              }
            }}
            title="Chỉnh sửa"
            className="p-1 hover:bg-slate-200 rounded text-slate-500"
          >
            <Edit2 size={14} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (isFolder) {
                openDialog("delete-folder", folder);
              } else {
                openDialog("delete-doc", { id: folder.id, name: folder.name });
              }
            }}
            title="Xóa"
            className="p-1 hover:bg-red-100 rounded text-red-500"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {isFolder && isOpen && hasChildren && (
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
  const rootItems = folders.filter((f) => !f.parentId);

  useEffect(() => {
    fetchFolders();
  }, [fetchFolders]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4 px-2 shrink-0">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Cây thư mục</h3>
        <button
          onClick={() => openDialog("add-folder", { parentId: null })}
          className="p-1 hover:bg-blue-50 text-blue-600 rounded-lg transition-colors"
          title="Thêm thư mục gốc"
        >
          <Plus size={16} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar min-h-0 pb-4 space-y-1 pr-1">
        {rootItems.length > 0 ? (
          rootItems.map((folder) => <FolderNode key={folder.id} folder={folder} />)
        ) : (
          <div className="text-center py-8 px-4 border-2 border-dashed border-slate-100 rounded-2xl mx-1">
            <Folder size={24} className="mx-auto text-slate-200 mb-2" />
            <p className="text-xs text-slate-400">Chưa có thư mục nào</p>
          </div>
        )}
      </div>
    </div>
  );
};
