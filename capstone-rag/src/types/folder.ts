export interface FolderDTO {
  id?: string;
  name?: string;
  parentId?: string;
  createdAt?: string;
}

export interface FolderUpsertDTO {
  id?: string;
  name?: string;
  parentId?: string;
}

export interface SystemNodeDTO {
  id: string;
  name: string;
  parentId: string | null;
  type: "FOLDER" | "DOCUMENT";
  tagIds: string[];
}
