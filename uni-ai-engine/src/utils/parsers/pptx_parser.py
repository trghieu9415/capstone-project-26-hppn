import io
from pptx import Presentation
from base import BaseParser
from utils.logger import app_logger


class PptxParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            stream = io.BytesIO(file_bytes)
            prs = Presentation(stream)
            text_parts = []

            for slide_num, slide in enumerate(prs.slides, 1):
                slide_text = []
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text.strip():
                        slide_text.append(shape.text.strip())

                if slide_text:
                    text_parts.append(f"--- Nội dung Slide {slide_num} ---")
                    text_parts.append("\n".join(slide_text))
                    text_parts.append("\n")

            return "\n".join(text_parts)
        except Exception as e:
            app_logger.error(f"[Error] Lỗi đọc PPTX: {e}")
            return ""
