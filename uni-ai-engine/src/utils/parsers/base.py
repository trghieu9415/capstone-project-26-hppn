import io
from abc import ABC, abstractmethod
from PIL import Image
import pytesseract
from utils.logger import app_logger


class BaseParser(ABC):
    @abstractmethod
    def extract_text(self, file_bytes: bytes) -> str:
        pass

    @staticmethod
    def ocr_image_bytes(image_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image, lang='vie+eng')
            return text.strip()
        except Exception as e:
            app_logger.warning(f"[OCR Warning] Bỏ qua ảnh vì lỗi nhận diện: {e}")
            return ""
