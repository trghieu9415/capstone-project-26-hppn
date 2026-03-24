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
import { SystemNodeDTO } from "@/types/folder";
import { TagDTO } from "@/types/tag";
import { DocumentDTO } from "@/types/document";
import { useToastStore } from "@/stores/useToastStore";

export const GlobalDialogs: React.FC = () => {
  const { activeDialog, dialogData, closeDialog } = useUIStore();
  // Actions
  const { clearChat } = useChatStore();
  const {
    deleteFolder,
    createFolder,
    updateFolder,
    addFolderItem,
    updateFolderItem,
    removeFolderItem,
    removeTagFromAllItems,
  } = useFolderStore();
  const { deleteTag, createTag, updateTag } = useTagStore();
  const { deleteDocument, updateDocumentMetadata, uploadDocument, isUploading } = useDocumentStore();

  const { addToast } = useToastStore();
  const folders = useFolderStore((state) => state.folders);
  const tags = useTagStore((state) => state.tags);

  if (!activeDialog) return null;

  return (
    <>
      <ConfirmDialog
        isOpen={activeDialog === "clear-chat"}
        onClose={closeDialog}
        onConfirm={() => {
          clearChat();
          addToast("Đã làm mới đoạn chat", "success");
        }}
        title="Làm mới cuộc trò chuyện"
        description="Bạn có chắc chắn muốn xóa toàn bộ nội dung cuộc trò chuyện này không? Nội dung sau khi xóa sẽ không thể khôi phục."
        variant="danger"
      />

      <ConfirmDialog
        isOpen={activeDialog === "delete-folder"}
        onClose={closeDialog}
        onConfirm={() => {
          deleteFolder((dialogData as SystemNodeDTO).id);
          closeDialog();
          addToast("Đã xóa thư mục", "success");
        }}
        title="Xác nhận xóa thư mục"
        description={`Hành động này không thể hoàn tác. Bạn có chắc chắn muốn xóa thư mục "${(dialogData as SystemNodeDTO)?.name}" và toàn bộ nội dung bên trong?`}
        variant="danger"
      />

      <ConfirmDialog
        isOpen={activeDialog === "delete-tag"}
        onClose={closeDialog}
        onConfirm={async () => {
          try {
            const tagId = (dialogData as TagDTO).id;
            await deleteTag(tagId);
            removeTagFromAllItems(tagId);
            addToast("Đã xóa nhãn thành công", "success");
            closeDialog();
          } catch (error) {
            addToast(error.message || "Lỗi khi xóa nhãn", "error");
          }
        }}
        title="Xác nhận xóa nhãn"
        description={`Bạn có chắc chắn muốn xóa nhãn "${(dialogData as TagDTO)?.name}"?`}
        variant="danger"
      />

      <ConfirmDialog
        isOpen={activeDialog === "delete-doc"}
        onClose={closeDialog}
        onConfirm={async () => {
          try {
            const docId = (dialogData as DocumentDTO).id!;
            await deleteDocument(docId);
            removeFolderItem(docId);
            addToast("Đã xóa tài liệu thành công", "success");
            closeDialog();
          } catch (error) {
            addToast(error.message || "Lỗi khi xóa tài liệu", "error");
          }
        }}
        title="Xác nhận xóa tài liệu"
        description={`Bạn có chắc chắn muốn xóa tài liệu "${(dialogData as DocumentDTO)?.name}"?`}
        variant="danger"
      />

      <FolderDialog
        isOpen={activeDialog === "add-folder" || activeDialog === "rename-folder"}
        onClose={closeDialog}
        onSave={async (name, parentId) => {
          try {
            if (activeDialog === "add-folder") {
              await createFolder({ name, parentId });
              addToast("Đã tạo thư mục mới", "success");
            } else {
              await updateFolder((dialogData as SystemNodeDTO).id!, { name, parentId });
              addToast("Cập nhật thư mục thành công", "success");
            }
            closeDialog();
          } catch (error) {
            addToast(error.message || "Lỗi khi xử lý thư mục", "error");
          }
        }}
        title={activeDialog === "add-folder" ? "Thêm thư mục mới" : "Đổi tên thư mục"}
        initialName={activeDialog === "rename-folder" ? (dialogData as SystemNodeDTO)?.name : ""}
        initialParentId={
          activeDialog === "add-folder"
            ? (dialogData as { parentId: string | null })?.parentId
            : (dialogData as SystemNodeDTO)?.parentId
        }
        folders={folders}
        currentFolderId={activeDialog === "rename-folder" ? (dialogData as SystemNodeDTO)?.id : undefined}
      />

      <TagDialog
        isOpen={activeDialog === "add-tag" || activeDialog === "edit-tag"}
        onClose={closeDialog}
        onSave={async (name, color) => {
          try {
            if (activeDialog === "add-tag") {
              await createTag({ name, color });
              addToast("Tạo nhãn thành công", "success");
            } else {
              await updateTag((dialogData as TagDTO).id, { name, color });
              addToast("Cập nhật nhãn thành công", "success");
            }
            closeDialog();
          } catch (error) {
            addToast(error.message || "Lỗi khi xử lý nhãn", "error");
          }
        }}
        title={activeDialog === "add-tag" ? "Thêm nhãn mới" : "Chỉnh sửa nhãn"}
        initialName={activeDialog === "edit-tag" ? (dialogData as TagDTO)?.name : ""}
        initialColor={activeDialog === "edit-tag" ? (dialogData as TagDTO)?.color : undefined}
      />

      {activeDialog === "edit-doc" && (
        <DocumentFormDialog
          isOpen={true}
          onClose={closeDialog}
          onSave={async (id, name, folderId, tagIds) => {
            try {
              await updateDocumentMetadata(id, { folder: folderId, tags: tagIds, name });
              updateFolderItem(id, { name, parentId: folderId, tagIds });
              addToast("Cập nhật tài liệu thành công", "success");
              closeDialog();
            } catch (error) {
              addToast(error.message || "Lỗi khi cập nhật tài liệu", "error");
            }
          }}
          document={dialogData as DocumentDTO}
          folders={folders}
          tags={tags}
        />
      )}

      <DocumentUploadDialog
        isOpen={activeDialog === "upload-doc"}
        onClose={closeDialog}
        onUpload={async (file, folderId) => {
          try {
            const newDoc = await uploadDocument(folderId, file);
            addFolderItem({
              id: newDoc.id,
              name: newDoc.name,
              parentId: folderId,
              type: "DOCUMENT",
              tagIds: newDoc.tags?.map((t) => t.id!) || [],
            });
            addToast("Tải tài liệu lên thành công!", "success");
            closeDialog();
          } catch (error) {
            addToast(error.message || "Upload thất bại. Vui lòng thử lại.", "error");
          }
        }}
        folders={folders}
        tags={tags}
        isUploading={isUploading} // TRUYỀN PROP VÀO ĐÂY
      />
    </>
  );
};
