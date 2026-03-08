from typing import List, Optional

from infrastructure.storage.base import IKeywordStore
from schemas.document import ChildNode
from schemas.request import DocumentFilter
from utils.logger import app_logger


class KeywordRetriever:
    def __init__(self, keyword_store: IKeywordStore):
        self.keyword_store = keyword_store

    async def retrieve(
        self, query: str, top_k: int = 5, filters: Optional[DocumentFilter] = None
    ) -> List[ChildNode]:
        if not query.strip():
            return []

        try:
            results = await self.keyword_store.search_keyword(
                query, top_k=top_k, filters=filters
            )
            return results
        except Exception as e:
            app_logger.error(f"Lỗi trong quá trình Keyword Retrieval: {e}")
            return []
