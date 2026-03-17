import React from "react";
import { Folder, FileText, Tag, Database } from "lucide-react";
import { cn } from "../../lib/utils";
import { useUIStore } from "@/stores/useUIStore";
import { FolderManager } from "../features/management/FolderManager";
import { DocumentManager } from "../features/management/DocumentManager";
import { TagManager } from "../features/management/TagManager";

type TabType = "folders" | "documents" | "tags";

export const Sidebar: React.FC = () => {
  const activeTab = useUIStore((state) => state.activeTab);
  const setActiveTab = useUIStore((state) => state.setActiveTab);

  // Strategy Pattern for Tab Content
  const TAB_CONTENT: Record<TabType, React.ReactNode> = {
    folders: <FolderManager />,
    documents: <DocumentManager />,
    tags: <TagManager />,
  };

  return (
    <aside className="w-80 bg-slate-50/50 border-r border-slate-200 flex flex-col h-full overflow-hidden">
      <div className="p-6">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-200">
            <Database className="text-white" size={20} />
          </div>
          <div>
            <h1 className="text-lg font-black text-slate-800 tracking-tight leading-none">UniRAG</h1>
            <p className="text-[10px] font-bold text-blue-600 uppercase tracking-widest mt-1">Knowledge Base</p>
          </div>
        </div>

        <nav className="flex p-1.5 bg-slate-100 rounded-2xl mb-8">
          {(["folders", "documents", "tags"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                "flex-1 flex items-center justify-center py-2 rounded-xl transition-all",
                activeTab === tab ? "bg-white text-blue-600 shadow-sm" : "text-slate-400 hover:text-slate-600"
              )}
            >
              {tab === "folders" && <Folder size={18} />}
              {tab === "documents" && <FileText size={18} />}
              {tab === "tags" && <Tag size={18} />}
            </button>
          ))}
        </nav>

        <div className="overflow-y-auto flex-1 custom-scrollbar pr-1">{TAB_CONTENT[activeTab]}</div>
      </div>
    </aside>
  );
};
