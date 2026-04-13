from utils.parsers.docx_parser import DocxParser
from utils.parsers.pdf_parser import PdfParser
from utils.parsers.pptx_parser import PptxParser
from utils.parsers.xlsx_parser import XlsxParser


class ParserFactory:
    @staticmethod
    def get_parser(extension: str):
        match extension.lower():
            case ".pdf":
                return PdfParser()
            case ".docx":
                return DocxParser()
            case ".pptx":
                return PptxParser()
            case ".xlsx":
                return XlsxParser()
            case _:
                raise ValueError(f"Định dạng {extension} chưa hỗ trợ!")
