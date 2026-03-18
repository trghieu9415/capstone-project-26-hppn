import React from "react";
import { Dialog } from "./Dialog";

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  variant?: "danger" | "primary";
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = "Xác nhận",
  cancelText = "Hủy",
  variant = "primary",
}) => {
  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      description={description}
      footer={
        <>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
          >
            {cancelText}
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className={`px-4 py-2 text-sm font-medium text-white rounded-xl transition-all shadow-sm ${
              variant === "danger"
                ? "bg-red-600 hover:bg-red-700 shadow-red-200"
                : "bg-blue-600 hover:bg-blue-700 shadow-blue-200"
            }`}
          >
            {confirmText}
          </button>
        </>
      }
    />
  );
};
