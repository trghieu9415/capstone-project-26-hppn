from utils.parsers import ParserFactory
from utils.text_processing import clean_text_pipeline


class DocumentLoader:
    def load_and_clean(self, file_bytes: bytes, extension: str) -> str:
        parser = ParserFactory.get_parser(extension)
        raw_text = parser.extract_text(file_bytes)

        if not raw_text:
            raise ValueError(f"Không thể trích xuất nội dung từ định dạng {extension}")

        clean_text = clean_text_pipeline(raw_text)

        return clean_text
