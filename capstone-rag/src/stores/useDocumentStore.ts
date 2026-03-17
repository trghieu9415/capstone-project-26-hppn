import { create } from "zustand";
import { DocumentDTO, DocumentUpdateDTO } from "@/types/document";
import { documentService } from "../services/documentService";

interface DocumentState {
  currentDocument: DocumentDTO | null;
  isUploading: boolean;
  isLoading: boolean;
  error: string | null;

  getDocument: (id: string) => Promise<void>;
  uploadDocument: (folderId: string, file: File) => Promise<DocumentDTO>;
  updateDocumentMetadata: (id: string, data: DocumentUpdateDTO) => Promise<void>;
  deleteDocument: (id: string) => Promise<void>;
}

export const useDocumentStore = create<DocumentState>((set) => ({
  currentDocument: null,
  isUploading: false,
  isLoading: false,
  error: null,

  getDocument: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      const doc = await documentService.getById(id);
      set({ currentDocument: doc, isLoading: false });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi tải tài liệu";
      set({ error: errorMessage, isLoading: false });
    }
  },

  uploadDocument: async (folderId: string, file: File) => {
    set({ isUploading: true, error: null });
    try {
      const newDoc = await documentService.create(folderId, file);
      set({ currentDocument: newDoc, isUploading: false });
      return newDoc;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi tải lên tài liệu";
      set({ error: errorMessage, isUploading: false });
      throw error;
    }
  },

  updateDocumentMetadata: async (id: string, data: DocumentUpdateDTO) => {
    set({ isLoading: true, error: null });
    try {
      const updatedDoc = await documentService.updateMetadata(id, data);
      set({ currentDocument: updatedDoc, isLoading: false });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi cập nhật siêu dữ liệu";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  deleteDocument: async (id: string) => {
    set({ isLoading: true, error: null });
    try {
      await documentService.delete(id);
      set({ currentDocument: null, isLoading: false });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi xóa tài liệu";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },
}));
