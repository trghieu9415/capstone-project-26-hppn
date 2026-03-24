import { create } from "zustand";
import { FolderUpsertDTO, SystemNodeDTO } from "@/types/folder";
import { folderService } from "@/services/folderService";

interface FolderState {
  folders: SystemNodeDTO[];
  isLoading: boolean;
  error: string | null;

  fetchFolders: () => Promise<void>;
  createFolder: (data: FolderUpsertDTO) => Promise<void>;
  updateFolder: (id: string, data: FolderUpsertDTO) => Promise<void>;
  deleteFolder: (id: string) => Promise<void>;

  addFolderItem: (item: SystemNodeDTO) => void;
  updateFolderItem: (id: string, data: Partial<SystemNodeDTO>) => void;
  removeFolderItem: (id: string) => void;
  removeTagFromAllItems: (tagId: string) => void;
}

export const useFolderStore = create<FolderState>((set, get) => ({
  folders: [],
  isLoading: false,
  error: null,

  fetchFolders: async () => {
    set({ isLoading: true, error: null });
    try {
      const folders = await folderService.getSystemNodes();
      set({ folders, isLoading: false });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi tải thư mục";
      set({ error: errorMessage, isLoading: false });
    }
  },

  createFolder: async (data: FolderUpsertDTO) => {
    set({ isLoading: true, error: null });
    try {
      const newFolder = await folderService.create(data);
      const systemNode: SystemNodeDTO = {
        id: newFolder.id!,
        name: newFolder.name!,
        parentId: newFolder.parentId || null,
        type: "FOLDER",
        tagIds: [],
      };
      set({ folders: [...get().folders, systemNode], isLoading: false });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi tạo thư mục";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  updateFolder: async (id: string, data: FolderUpsertDTO) => {
    set({ isLoading: true, error: null });
    try {
      const updatedFolder = await folderService.update(id, data);
      const systemNode: SystemNodeDTO = {
        id: updatedFolder.id!,
        name: updatedFolder.name!,
        parentId: updatedFolder.parentId || null,
        type: "FOLDER",
        tagIds: [],
      };
      set({
        folders: get().folders.map((folder) => (folder.id === id ? systemNode : folder)),
        isLoading: false,
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi cập nhật thư mục";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  deleteFolder: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await folderService.delete(id);
      set({
        folders: get().folders.filter((folder) => folder.id !== id),
        isLoading: false,
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi xóa thư mục";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  addFolderItem: (item) => set((state) => ({ folders: [...state.folders, item] })),

  updateFolderItem: (id, data) =>
    set((state) => ({
      folders: state.folders.map((f) => (f.id === id ? { ...f, ...data } : f)),
    })),

  removeFolderItem: (id) =>
    set((state) => ({
      folders: state.folders.filter((f) => f.id !== id),
    })),

  removeTagFromAllItems: (tagId) =>
    set((state) => ({
      folders: state.folders.map((f) => ({
        ...f,
        tagIds: f.tagIds?.filter((id) => id !== tagId) || [],
      })),
    })),
}));
