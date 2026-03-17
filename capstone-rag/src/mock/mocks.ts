import { Folder, Document, Tag } from "@/types";

// --- Mock Data ---
export const INITIAL_FOLDERS: Folder[] = [
  { id: "1", name: "Quy chế đào tạo", parentId: null },
  { id: "2", name: "Năm học 2023-2024", parentId: "1" },
  { id: "3", name: "Biểu mẫu sinh viên", parentId: null },
];

export const INITIAL_TAGS: Tag[] = [
  { id: "t1", name: "Quan trọng", color: "bg-red-100 text-red-700" },
  { id: "t2", name: "Học vụ", color: "bg-blue-100 text-blue-700" },
  { id: "t3", name: "Mới", color: "bg-green-100 text-green-700" },
];

export const INITIAL_DOCS: Document[] = [
  {
    id: "d1",
    name: "Quy che hoc vu SGU 2023",
    extension: "pdf",
    createdAt: "2023-10-15",
    folderId: "2",
    tagIds: ["t1", "t2"],
  },
  {
    id: "d2",
    name: "Don xin thoi hoc",
    extension: "docx",
    createdAt: "2023-11-20",
    folderId: "3",
    tagIds: ["t2"],
  },
];
