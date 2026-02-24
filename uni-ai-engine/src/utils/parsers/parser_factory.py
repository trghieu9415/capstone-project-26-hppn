from .pdf_parser import PdfParser
from .docx_parser import DocxParser
from .pptx_parser import PptxParser
from .xlsx_parser import XlsxParser


class ParserFactory:
    @staticmethod
    def get_parser(extension: str):
        ext = extension.lower()
        if ext == ".pdf":
            return PdfParser()
        elif ext in [".docx", ".doc"]:
            return DocxParser()
        elif ext in [".pptx", ".ppt"]:
            return PptxParser()
        elif ext in [".xlsx", ".xls", ".csv"]:
            return XlsxParser()
        else:
            raise ValueError(f"Định dạng {ext} chưa được hỗ trợ!")
