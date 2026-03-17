export interface Folder {
  id: string;
  name: string;
  parentId: string | null;
}

export interface Tag {
  id: string;
  name: string;
  color: string;
}

export interface Document {
  id: string;
  name: string;
  extension: string;
  createdAt: string;
  folderId: string;
  tagIds: string[];
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

export interface ContextFilters {
  docIds: string[];
  folderIds: string[];
  tagIds: string[];
}

export type DialogState =
  | "delete-folder"
  | "rename-folder"
  | "add-folder"
  | "delete-tag"
  | "add-tag"
  | "edit-tag"
  | "delete-doc"
  | "edit-doc"
  | "clear-chat"
  | null;

export type FolderDialogState = "delete-folder" | "rename-folder" | "add-folder";
export type TagDialogState = "delete-tag" | "add-tag" | "edit-tag";
export type DocumentDialogState = "delete-doc" | "edit-doc";
export type ChatDialogState = "clear-chat";
