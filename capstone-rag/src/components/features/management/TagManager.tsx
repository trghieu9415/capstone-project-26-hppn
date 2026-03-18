import React, { useEffect } from "react";
import { Plus, Trash2, Edit2, Tag } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTagStore } from "@/stores/useTagStore";
import { useUIStore } from "@/stores/useUIStore";

export const TagManager: React.FC = () => {
  const { tags, fetchTags } = useTagStore();
  const { openDialog } = useUIStore();

  useEffect(() => {
    fetchTags();
  }, [fetchTags]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between px-2">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Nhãn</h3>
        <button
          onClick={() => openDialog("add-tag")}
          className="p-1 hover:bg-blue-50 text-blue-600 rounded-lg transition-colors"
          title="Thêm nhãn mới"
        >
          <Plus size={16} />
        </button>
      </div>

      <div className="grid grid-cols-1 gap-2 px-1">
        {tags.length > 0 ? (
          tags.map((tag) => (
            <div
              key={tag.id}
              className="group flex items-center justify-between p-3 bg-white border border-slate-100 rounded-2xl hover:shadow-md hover:shadow-slate-200/50 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className={cn("w-3 h-3 rounded-full shadow-inner")} />
                <span className={cn("text-xs font-bold uppercase tracking-wider")}>{tag.name}</span>
              </div>
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => openDialog("edit-tag", tag)}
                  className="p-1.5 hover:bg-slate-50 rounded-lg text-slate-400 hover:text-blue-600 transition-colors"
                >
                  <Edit2 size={14} />
                </button>
                <button
                  onClick={() => openDialog("delete-tag", tag)}
                  className="p-1.5 hover:bg-red-50 rounded-lg text-slate-400 hover:text-red-600 transition-colors"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12 bg-slate-50/50 rounded-3xl border-2 border-dashed border-slate-100">
            <Tag size={24} className="mx-auto text-slate-200 mb-2" />
            <p className="text-xs text-slate-400">Chưa có nhãn nào</p>
          </div>
        )}
      </div>
    </div>
  );
};
