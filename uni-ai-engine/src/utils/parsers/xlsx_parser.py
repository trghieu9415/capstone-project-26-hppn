import io
import pandas as pd
from utils.parsers.base import BaseParser
from utils.loggers.app_logger import app_logger


class XlsxParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            stream = io.BytesIO(file_bytes)
            dfs = pd.read_excel(stream, sheet_name=None, engine='openpyxl')

            text_parts = []
            for sheet_name, df in dfs.items():
                if df.empty:
                    continue

                text_parts.append(f"### Tên Sheet: {sheet_name}")
                df = df.dropna(how="all").dropna(axis=1, how="all")
                df = df.reset_index(drop=True)

                table_markdown = df.to_markdown(index=False, na_rep="")
                text_parts.append(table_markdown)
                text_parts.append("\n" + "=" * 3 + "\n")

            return "\n".join(text_parts)
        except Exception as e:
            app_logger.error(f"[Error] Lỗi đọc XLSX: {e}")
            return ""
