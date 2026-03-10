import fitz
from utils.parsers.base import BaseParser
from utils.logger import app_logger


class PdfParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_parts = []

            for page in doc:
                text_parts.append(page.get_text("text"))

            doc.close()
            return "\n".join(text_parts)
        except Exception as e:
            app_logger.error(f"[Error] Lỗi đọc PDF từ byte stream: {e}")
            return ""
