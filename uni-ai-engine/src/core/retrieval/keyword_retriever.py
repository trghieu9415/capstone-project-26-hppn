from typing import List, Optional
from uuid import UUID

from configs.settings import settings
from infrastructure.storage.base import IKeywordStore
from schemas.document import ScoredNode
from utils.loggers.app_logger import app_logger
from utils.loggers.retrieval_logger import retrieval_logger


class KeywordRetriever:
    def __init__(self, keyword_store: IKeywordStore):
        self.keyword_store = keyword_store

    async def retrieve(
        self,
        query: str,
        top_k: int = settings.KEYWORD_SEARCH_TOP_K,
        doc_ids: Optional[List[UUID]] = None
    ) -> List[ScoredNode]:

        try:
            app_logger.info(f"--- Keyword Retrieval (BM25): '{query[:50]}...' ---")
            results = await self.keyword_store.search_keyword(
                query=query,
                top_k=top_k,
                doc_ids=doc_ids
            )

            app_logger.info(
                f"-> Keyword search hoàn tất. Tìm thấy {len(results)} chunks.")
            return results

        except Exception as e:
            app_logger.error(f"Lỗi trong KeywordRetriever: {e}")
            return []
