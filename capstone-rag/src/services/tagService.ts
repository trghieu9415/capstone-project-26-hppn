// tagService.ts
import { TagDTO, TagUpsertDTO } from "@/types/tag";
import apiClient from "./_client";

export const tagService = {
  getAll: async (): Promise<TagDTO[]> => {
    const response = await apiClient.get("/api/tags");
    return response.data;
  },

  getById: async (id: string): Promise<TagDTO> => {
    const response = await apiClient.get(`/api/tags/${id}`);
    return response.data;
  },

  create: async (data: TagUpsertDTO): Promise<TagDTO> => {
    const response = await apiClient.post("/api/tags", data);
    return response.data;
  },

  update: async (id: string, data: TagUpsertDTO): Promise<TagDTO> => {
    const response = await apiClient.put(`/api/tags/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/tags/${id}`);
  },
};
