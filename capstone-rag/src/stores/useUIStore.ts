import { create } from "zustand";

export type DialogType =
  | "add-folder"
  | "rename-folder"
  | "delete-folder"
  | "add-tag"
  | "edit-tag"
  | "delete-tag"
  | "edit-doc"
  | "delete-doc"
  | "upload-doc"
  | "clear-chat"
  | null;

interface UIState {
  activeTab: "folders" | "documents" | "tags";
  activeDialog: DialogType;
  dialogData: unknown;
  showFilters: boolean;
  selectedFolderId: string | null;

  setActiveTab: (tab: "folders" | "documents" | "tags") => void;
  openDialog: (type: DialogType, data?: unknown) => void;
  closeDialog: () => void;
  setShowFilters: (show: boolean) => void;
  setSelectedFolderId: (id: string | null) => void;
}

export const useUIStore = create<UIState>((set) => ({
  activeTab: "folders",
  activeDialog: null,
  dialogData: null,
  showFilters: false,
  selectedFolderId: null,

  setActiveTab: (tab) => set({ activeTab: tab }),
  openDialog: (type, data = null) => set({ activeDialog: type, dialogData: data }),
  closeDialog: () => set({ activeDialog: null, dialogData: null }),
  setShowFilters: (show) => set({ showFilters: show }),
  setSelectedFolderId: (id) => set({ selectedFolderId: id }),
}));
