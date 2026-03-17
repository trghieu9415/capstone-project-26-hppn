export interface DocumentFolder {
  id?: string;
  name?: string;
  parent?: DocumentFolder;
}

export interface DocumentTag {
  id?: string;
  name?: string;
}

export interface DocumentDTO {
  id?: string;
  folder?: DocumentFolder;
  tags?: DocumentTag[];
  name?: string;
  extension?: string;
  createdAt?: string;
}

export interface DocumentUpdateDTO {
  folder?: string;
  tags?: string[];
  name?: string;
}

export interface ContextFilters {
  docIds: string[];
  folderIds: string[];
  tagIds: string[];
}
