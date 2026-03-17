import React from "react";
import { useUIStore } from "@/stores/useUIStore";
import { useChatStore } from "@/stores/useChatStore";
import { useFolderStore } from "@/stores/useFolderStore";
import { useTagStore } from "@/stores/useTagStore";
import { useDocumentStore } from "@/stores/useDocumentStore";
import { ConfirmDialog } from "../../shared/ConfirmDialog";
import { FolderDialog } from "./FolderDialog";
import { TagDialog } from "./TagDialog";
import { DocumentFormDialog } from "./DocumentFormDialog";
import { DocumentUploadDialog } from "./DocumentUploadDialog";
import { FolderDTO } from "@/types/folder";
import { TagDTO } from "@/types/tag";
import { DocumentDTO } from "@/types/document";

export const GlobalDialogs: React.FC = () => {
  const { activeDialog, dialogData, closeDialog } = useUIStore();
  // Actions
  const { clearChat } = useChatStore();
  const { deleteFolder, createFolder, updateFolder } = useFolderStore();
  const { deleteTag, createTag, updateTag } = useTagStore();
  const { deleteDocument, updateDocumentMetadata, uploadDocument } = useDocumentStore();

  // Data for dialogs
  const folders = useFolderStore((state) => state.folders);
  const tags = useTagStore((state) => state.tags);

  if (!activeDialog) return null;

  return (
    <>
      <ConfirmDialog
        isOpen={activeDialog === "clear-chat"}
        onClose={closeDialog}
        onConfirm={clearChat}
        title="Làm mới cuộc trò chuyện"
        description="Bạn có chắc chắn muốn xóa toàn bộ nội dung cuộc trò chuyện này không? Nội dung sau khi xóa sẽ không thể khôi phục."
        variant="danger"
      />

      <ConfirmDialog
        isOpen={activeDialog === "delete-folder"}
        onClose={closeDialog}
        onConfirm={() => {
          deleteFolder((dialogData as FolderDTO).id);
          closeDialog();
        }}
        title="Xác nhận xóa thư mục"
        description={`Hành động này không thể hoàn tác. Bạn có chắc chắn muốn xóa thư mục "${(dialogData as FolderDTO)?.name}" và toàn bộ nội dung bên trong?`}
        variant="danger"
      />

      <ConfirmDialog
        isOpen={activeDialog === "delete-tag"}
        onClose={closeDialog}
        onConfirm={() => {
          deleteTag((dialogData as TagDTO).id);
          closeDialog();
        }}
        title="Xác nhận xóa nhãn"
        description={`Bạn có chắc chắn muốn xóa nhãn "${(dialogData as TagDTO)?.name}"?`}
        variant="danger"
      />

      <ConfirmDialog
        isOpen={activeDialog === "delete-doc"}
        onClose={closeDialog}
        onConfirm={() => {
          deleteDocument((dialogData as DocumentDTO).id);
          closeDialog();
        }}
        title="Xác nhận xóa tài liệu"
        description={`Bạn có chắc chắn muốn xóa tài liệu "${(dialogData as DocumentDTO)?.name}"?`}
        variant="danger"
      />

      <FolderDialog
        isOpen={activeDialog === "add-folder" || activeDialog === "rename-folder"}
        onClose={closeDialog}
        onSave={(name, parentId) => {
          if (activeDialog === "add-folder") {
            createFolder({ name, parentId });
          } else {
            updateFolder((dialogData as FolderDTO).id, { name, parentId });
          }
          closeDialog();
        }}
        title={activeDialog === "add-folder" ? "Thêm thư mục mới" : "Đổi tên thư mục"}
        initialName={activeDialog === "rename-folder" ? (dialogData as FolderDTO)?.name : ""}
        initialParentId={
          activeDialog === "add-folder"
            ? (dialogData as { parentId: string | null })?.parentId
            : (dialogData as FolderDTO)?.parentId
        }
        folders={folders}
        currentFolderId={activeDialog === "rename-folder" ? (dialogData as FolderDTO)?.id : undefined}
      />

      <TagDialog
        isOpen={activeDialog === "add-tag" || activeDialog === "edit-tag"}
        onClose={closeDialog}
        onSave={(name, color) => {
          if (activeDialog === "add-tag") {
            createTag({ name, color });
          } else {
            updateTag((dialogData as TagDTO).id, { name, color });
          }
          closeDialog();
        }}
        title={activeDialog === "add-tag" ? "Thêm nhãn mới" : "Chỉnh sửa nhãn"}
        initialName={activeDialog === "edit-tag" ? (dialogData as TagDTO)?.name : ""}
        initialColor={activeDialog === "edit-tag" ? (dialogData as TagDTO)?.color : undefined}
      />

      {activeDialog === "edit-doc" && (
        <DocumentFormDialog
          isOpen={true}
          onClose={closeDialog}
          onSave={(id, name, folder, tags) => {
            updateDocumentMetadata(id, { folder, tags, name });
            closeDialog();
          }}
          document={dialogData as DocumentDTO}
          folders={folders}
          tags={tags}
        />
      )}

      <DocumentUploadDialog
        isOpen={activeDialog === "upload-doc"}
        onClose={closeDialog}
        onUpload={(file, folderId) => {
          uploadDocument(folderId, file);
          closeDialog();
        }}
        folders={folders}
        tags={tags}
      />
    </>
  );
};
