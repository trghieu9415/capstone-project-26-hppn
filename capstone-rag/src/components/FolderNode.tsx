import { cn } from "@/lib/utils";
import { Folder } from "@/types";
import { useState } from "react";
import { ChevronDown, ChevronRight, FolderIcon, Plus, Edit2, Trash2 } from "lucide-react";

interface FolderNodeProps {
  folder: Folder;
  allFolders: Folder[];
  onAdd: (parentId: string) => void;
  onRename: (folder: Folder) => void;
  onDelete: (folder: Folder) => void;
  onSelect: (id: string) => void;
  selectedId: string | null;
  level?: number;
}

export const FolderNode = (props: FolderNodeProps) => {
  const { folder, allFolders, onAdd, onRename, onDelete, onSelect, selectedId, level = 0 } = props;

  const [isOpen, setIsOpen] = useState(true);
  const children = allFolders.filter((f) => f.parentId === folder.id);
  const hasChildren = children.length > 0;
  const isSelected = selectedId === folder.id;

  return (
    <div className="select-none">
      <div
        onClick={() => onSelect(folder.id)}
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
        <FolderIcon size={16} className={cn("mr-2 shrink-0", isSelected ? "text-blue-600" : "text-blue-400")} />
        <span className="text-sm flex-1 truncate font-medium">{folder.name}</span>

        <div className="hidden group-hover:flex items-center gap-1 ml-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onAdd(folder.id);
            }}
            title="Thêm thư mục con"
            className="p-1 hover:bg-blue-200 rounded text-blue-600"
          >
            <Plus size={14} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onRename(folder);
            }}
            title="Đổi tên"
            className="p-1 hover:bg-slate-200 rounded text-slate-500"
          >
            <Edit2 size={14} />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(folder);
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
            <FolderNode
              key={child.id}
              folder={child}
              allFolders={allFolders}
              onAdd={onAdd}
              onRename={onRename}
              onDelete={onDelete}
              onSelect={onSelect}
              selectedId={selectedId}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};
