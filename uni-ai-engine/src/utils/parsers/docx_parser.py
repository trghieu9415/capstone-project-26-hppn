import io
from docx import Document
from utils.logger import app_logger
from utils.parsers.base import BaseParser


class DocxParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            stream = io.BytesIO(file_bytes)
            doc = Document(stream)
            text_parts = []

            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text.strip())

            for table in doc.tables:
                text_parts.append("\n[Bắt đầu bảng]")
                for row in table.rows:
                    row_data = [cell.text.replace("\n", " ").strip() for cell in
                                row.cells]
                    if any(row_data):
                        text_parts.append(" | ".join(row_data))
                text_parts.append("[Kết thúc bảng]\n")

            return "\n".join(text_parts)
        except Exception as e:
            app_logger.error(f"[Error] Lỗi đọc DOCX: {e}")
            return ""
