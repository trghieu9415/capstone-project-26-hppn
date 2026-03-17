export interface ContextFilters {
  docIds: string[];
  folderIds: string[];
  tagIds: string[];
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

export interface QueryRequestDTO {
  question?: string;
  docIds?: string[];
  folderIds?: string[];
  tagIds?: string[];
}
