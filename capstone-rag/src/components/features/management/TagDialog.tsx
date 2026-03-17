import React, { useEffect, useState } from "react";
import { Dialog } from "../../shared/Dialog";

interface TagDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (name: string, color: string) => void;
  title: string;
  initialName?: string;
  initialColor?: string;
}

const COLORS = [
  { name: "Đỏ", value: "bg-red-100 text-red-700" },
  { name: "Xanh dương", value: "bg-blue-100 text-blue-700" },
  { name: "Xanh lá", value: "bg-green-100 text-green-700" },
  { name: "Vàng", value: "bg-yellow-100 text-yellow-700" },
  { name: "Tím", value: "bg-purple-100 text-purple-700" },
  { name: "Hồng", value: "bg-pink-100 text-pink-700" },
  { name: "Xám", value: "bg-slate-100 text-slate-700" },
];

export const TagDialog: React.FC<TagDialogProps> = ({
  isOpen,
  onClose,
  onSave,
  title,
  initialName = "",
  initialColor = COLORS[0].value,
}) => {
  const [name, setName] = useState(initialName);
  const [color, setColor] = useState(initialColor);

  useEffect(() => {
    if (isOpen) {
      setName(initialName);
      setColor(initialColor);
    }
  }, [isOpen, initialName, initialColor]);

  return (
    <Dialog
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      footer={
        <>
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
          >
            Hủy
          </button>
          <button
            onClick={() => onSave(name, color)}
            disabled={!name.trim()}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all shadow-sm shadow-blue-200"
          >
            Lưu
          </button>
        </>
      }
    >
      <div className="space-y-6">
        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tên nhãn</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Nhập tên nhãn..."
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            autoFocus
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Màu sắc</label>
          <div className="grid grid-cols-2 gap-2">
            {COLORS.map((c) => (
              <button
                key={c.value}
                onClick={() => setColor(c.value)}
                className={`flex items-center gap-2 p-2 rounded-xl border-2 transition-all ${
                  color === c.value
                    ? "border-blue-600 bg-blue-50 shadow-sm"
                    : "border-transparent bg-slate-50 hover:bg-slate-100"
                }`}
              >
                <div className={`w-4 h-4 rounded-full ${c.value.split(" ")[0]}`} />
                <span className="text-xs font-medium text-slate-600">{c.name}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </Dialog>
  );
};
