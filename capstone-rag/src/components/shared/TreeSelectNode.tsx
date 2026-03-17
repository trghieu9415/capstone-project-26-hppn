import React, { useState } from "react";
import { Folder, ChevronRight, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { FolderDTO } from "@/types/folder";

interface TreeSelectNodeProps {
  folder: FolderDTO;
  allFolders: FolderDTO[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  level?: number;
}

export const TreeSelectNode: React.FC<TreeSelectNodeProps> = ({
  folder,
  allFolders,
  selectedId,
  onSelect,
  level = 0,
}) => {
  const [isOpen, setIsOpen] = useState(true);
  const children = allFolders.filter((f) => f.parentId === folder.id);
  const hasChildren = children.length > 0;
  const isSelected = selectedId === folder.id;

  return (
    <div className="select-none">
      <div
        onClick={() => onSelect(folder.id)}
        className={cn(
          "flex items-center py-2 px-3 rounded-xl cursor-pointer transition-all mb-1",
          isSelected ? "bg-blue-600 text-white shadow-md" : "hover:bg-slate-100 text-slate-600",
          level > 0 && "ml-4"
        )}
      >
        <div
          onClick={(e) => {
            e.stopPropagation();
            setIsOpen(!isOpen);
          }}
          className="p-1 mr-1"
        >
          {hasChildren ? isOpen ? <ChevronDown size={14} /> : <ChevronRight size={14} /> : <div className="w-3.5" />}
        </div>
        <Folder size={16} className={cn("mr-2", isSelected ? "text-white" : "text-blue-400")} />
        <span className="text-sm font-medium truncate">{folder.name}</span>
      </div>
      {isOpen && hasChildren && (
        <div className="border-l border-slate-200 ml-4 pl-1">
          {children.map((child) => (
            <TreeSelectNode
              key={child.id}
              folder={child}
              allFolders={allFolders}
              selectedId={selectedId}
              onSelect={onSelect}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};
