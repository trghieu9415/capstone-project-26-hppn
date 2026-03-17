import { FolderDTO, FolderUpsertDTO } from "@/types/folder";
import apiClient from "./_client";

export const folderService = {
  getAll: async (): Promise<FolderDTO[]> => {
    const response = await apiClient.get("/api/folders");
    return response.data;
  },

  getById: async (id: string): Promise<FolderDTO> => {
    const response = await apiClient.get(`/api/folders/${id}`);
    return response.data;
  },

  create: async (data: FolderUpsertDTO): Promise<FolderDTO> => {
    const response = await apiClient.post("/api/folders", data);
    return response.data;
  },

  update: async (id: string, data: FolderUpsertDTO): Promise<FolderDTO> => {
    const response = await apiClient.put(`/api/folders/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/folders/${id}`);
  },
};
