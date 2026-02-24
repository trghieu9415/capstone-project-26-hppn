import fitz  # PyMuPDF
from .base import BaseParser


class PdfParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            # Mở luồng byte trực tiếp, khai báo rõ filetype="pdf"
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_parts = []

            for page in doc:
                # Có thể thêm cờ để trích xuất text tốt hơn nếu cần
                text_parts.append(page.get_text("text"))

            doc.close()
            return "\n".join(text_parts)
        except Exception as e:
            print(f"[Error] Lỗi đọc PDF từ byte stream: {e}")
            return ""
