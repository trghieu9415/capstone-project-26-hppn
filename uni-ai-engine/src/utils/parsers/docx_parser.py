import io
from docx import Document
from .base import BaseParser
from utils.logger import app_logger


class DocxParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            stream = io.BytesIO(file_bytes)
            doc = Document(stream)

            full_text = "\n".join([para.text for para in doc.paragraphs if para.text])
            return full_text
        except Exception as e:
            app_logger.error(f"[Error] Lỗi đọc DOCX: {e}")
            return ""
