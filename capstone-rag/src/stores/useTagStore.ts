import { create } from "zustand";
import { tagService } from "../services/tagService";
import { TagDTO, TagUpsertDTO } from "@/types/tag";

interface TagState {
  tags: TagDTO[];
  isLoading: boolean;
  error: string | null;

  fetchTags: () => Promise<void>;
  createTag: (data: TagUpsertDTO) => Promise<void>;
  updateTag: (id: string, data: TagUpsertDTO) => Promise<void>;
  deleteTag: (id: string) => Promise<void>;
}

export const useTagStore = create<TagState>((set, get) => ({
  tags: [],
  isLoading: false,
  error: null,

  fetchTags: async () => {
    set({ isLoading: true, error: null });
    try {
      const tags = await tagService.getAll();
      set({ tags, isLoading: false });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi tải danh sách thẻ";
      set({ error: errorMessage, isLoading: false });
    }
  },

  createTag: async (data: TagUpsertDTO) => {
    set({ isLoading: true, error: null });
    try {
      const newTag = await tagService.create(data);
      set({ tags: [...get().tags, newTag], isLoading: false });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi tạo thẻ";
      set({ error: errorMessage, isLoading: false });
      throw error; // Ném lỗi ra ngoài để UI có thể hiển thị Toast notification
    }
  },

  updateTag: async (id: string, data: TagUpsertDTO) => {
    set({ isLoading: true, error: null });
    try {
      const updatedTag = await tagService.update(id, data);
      set({
        tags: get().tags.map((tag) => (tag.id === id ? updatedTag : tag)),
        isLoading: false,
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi cập nhật thẻ";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  deleteTag: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await tagService.delete(id);
      set({
        tags: get().tags.filter((tag) => tag.id !== id),
        isLoading: false,
      });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi xóa thẻ";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },
}));
