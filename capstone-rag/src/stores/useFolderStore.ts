import { create } from "zustand";
import { FolderDTO, FolderUpsertDTO } from "@/types/folder";
import { folderService } from "../services/folderService";

interface FolderState {
  folders: FolderDTO[];
  isLoading: boolean;
  error: string | null;

  fetchFolders: () => Promise<void>;
  createFolder: (data: FolderUpsertDTO) => Promise<void>;
  updateFolder: (id: string, data: FolderUpsertDTO) => Promise<void>;
  deleteFolder: (id: string) => Promise<void>;
}

export const useFolderStore = create<FolderState>((set, get) => ({
  folders: [],
  isLoading: false,
  error: null,

  fetchFolders: async () => {
    set({ isLoading: true, error: null });
    try {
      const folders = await folderService.getAll();
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
      set({ folders: [...get().folders, newFolder], isLoading: false });
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
      set({
        folders: get().folders.map((folder) => (folder.id === id ? updatedFolder : folder)),
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
}));
