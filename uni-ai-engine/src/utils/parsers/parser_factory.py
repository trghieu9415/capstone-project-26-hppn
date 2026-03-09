from pdf_parser import PdfParser
from docx_parser import DocxParser
from pptx_parser import PptxParser
from xlsx_parser import XlsxParser


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
