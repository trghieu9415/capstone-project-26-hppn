import { create } from "zustand";
import { DocumentDTO, DocumentUpdateDTO, ContextFilters } from "@/types/document";
import { documentService } from "../services/documentService";

interface DocumentState {
  documents: DocumentDTO[];
  currentDocument: DocumentDTO | null;
  isUploading: boolean;
  isLoading: boolean;
  error: string | null;
  filters: ContextFilters;

  // Actions
  setFilters: (filters: ContextFilters) => void;
  getDocumentsByFolder: (folderId: string) => Promise<void>;
  getDocument: (id: string) => Promise<void>;
  uploadDocument: (folderId: string, file: File) => Promise<DocumentDTO>;
  updateDocumentMetadata: (id: string, data: DocumentUpdateDTO) => Promise<void>;
  deleteDocument: (id: string) => Promise<void>;
  createDocument: (doc: DocumentDTO) => void;
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  documents: [
    {
      id: "d1",
      name: "Quy che hoc vu SGU 2023",
      extension: "pdf",
      createdAt: new Date().toISOString(),
      folder: { id: "2", name: "Quy chế" },
      tags: [{ id: "t1", name: "Học vụ" }],
    },
  ],
  currentDocument: null,
  isUploading: false,
  isLoading: false,
  error: null,
  filters: { docIds: [], folderIds: [], tagIds: [] },

  setFilters: (filters) => set({ filters }),

  getDocumentsByFolder: async (folderId: string) => {
    set({ isLoading: true, error: null });
    try {
      const docs = await documentService.getByFolderId(folderId);
      set({ documents: docs, isLoading: false });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi tải danh sách tài liệu";
      set({ error: errorMessage, isLoading: false });
    }
  },

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
      // Cập nhật cả currentDocument và thêm vào danh sách chung
      set((state) => ({
        documents: [...state.documents, newDoc],
        currentDocument: newDoc,
        isUploading: false,
      }));
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
      set((state) => ({
        currentDocument: updatedDoc,
        // Cập nhật tài liệu cụ thể trong mảng documents
        documents: state.documents.map((d) => (d.id === id ? updatedDoc : d)),
        isLoading: false,
      }));
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
      set((state) => ({
        currentDocument: state.currentDocument?.id === id ? null : state.currentDocument,
        documents: state.documents.filter((d) => d.id !== id),
        isLoading: false,
      }));
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "Lỗi khi xóa tài liệu";
      set({ error: errorMessage, isLoading: false });
      throw error;
    }
  },

  createDocument: (doc) =>
    set((state) => ({
      documents: [...state.documents, doc],
    })),
}));
