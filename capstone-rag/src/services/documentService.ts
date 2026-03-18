import { DocumentDTO, DocumentUpdateDTO } from "@/types/document";
import apiClient from "./_client";

export const documentService = {
  getByFolderId: async (folderId: string): Promise<DocumentDTO[]> => {
    const response = await apiClient.get(`/api/documents/folder/${folderId}`);
    return response.data;
  },

  getAll: async (): Promise<DocumentDTO[]> => {
    const response = await apiClient.get("/api/documents");
    return response.data;
  },

  getById: async (id: string): Promise<DocumentDTO> => {
    const response = await apiClient.get(`/api/documents/${id}`);
    return response.data;
  },

  create: async (folderId: string, file: File): Promise<DocumentDTO> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post("/api/documents", formData, {
      params: { folder: folderId },
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  updateMetadata: async (id: string, data: DocumentUpdateDTO): Promise<DocumentDTO> => {
    const response = await apiClient.put(`/api/documents/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/documents/${id}`);
  },
};
