import io
import pandas as pd
from .base import BaseParser
from utils.logger import app_logger


class XlsxParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            stream = io.BytesIO(file_bytes)
            dfs = pd.read_excel(stream, sheet_name=None)

            text_parts = []
            for sheet_name, df in dfs.items():
                text_parts.append(f"### Bảng dữ liệu: {sheet_name}")

                df.dropna(how="all", inplace=True)
                df.dropna(axis=1, how="all", inplace=True)

                text_parts.append(df.to_markdown(index=False, na_rep=""))
                text_parts.append("\n")

            return "\n".join(text_parts)
        except Exception as e:
            app_logger.error(f"[Error] Lỗi đọc XLSX: {e}")
            return ""
