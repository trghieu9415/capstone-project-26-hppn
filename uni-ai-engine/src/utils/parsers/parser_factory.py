from utils.parsers.docx_parser import DocxParser
from utils.parsers.pdf_parser import PdfParser
from utils.parsers.pptx_parser import PptxParser
from utils.parsers.xlsx_parser import XlsxParser


class ParserFactory:
    @staticmethod
    def get_parser(extension: str):
        ext = extension.lower()
        if ext == ".pdf":
            return PdfParser()
        elif ext == ".docx":
            return DocxParser()
        elif ext == ".pptx":
            return PptxParser()
        elif ext == ".xlsx":
            return XlsxParser()
        else:
            raise ValueError(
                f"Định dạng {ext} chưa được hỗ trợ! Chỉ dùng: .pdf, .docx, .pptx, .xlsx")
