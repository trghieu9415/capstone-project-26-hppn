import fitz
from utils.parsers.base import BaseParser
from utils.loggers.app_logger import app_logger


class PdfParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_parts = []
            processed_images_hashes = set()

            for page_num, page in enumerate(doc):
                page_text = page.get_text("text").strip()
                if page_text:
                    text_parts.append(f"--- Trang {page_num + 1} ---\n{page_text}")

                image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    if xref in processed_images_hashes:
                        continue

                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]

                    ocr_result = self.ocr_image_bytes(image_bytes)

                    if ocr_result:
                        text_parts.append(
                            f"\n[Nội dung OCR từ ảnh trang {page_num + 1}]:\n{ocr_result}\n")

                    processed_images_hashes.add(xref)

            doc.close()
            return "\n".join(text_parts)

        except Exception as e:
            app_logger.error(f"[Error] Lỗi đọc PDF từ byte stream: {e}")
            return ""
