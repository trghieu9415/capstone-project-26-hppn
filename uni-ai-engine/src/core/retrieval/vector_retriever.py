from typing import List, Optional
from uuid import UUID

from infrastructure.storage.base import IVectorStore
from infrastructure.embeddings.base import IEmbeddingService
from schemas.document import ScoredNode
from utils.logger import app_logger


class VectorRetriever:
    def __init__(
        self,
        vector_store: IVectorStore,
        embedding_service: IEmbeddingService
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        doc_ids: Optional[List[UUID]] = None
    ) -> List[ScoredNode]:
        try:
            app_logger.info(f"--- Vector Retrieval: '{query[:50]}...' ---")
            query_embedding = await self.embedding_service.embed_query(query)

            if not query_embedding:
                app_logger.warning("Không thể tạo embedding cho query.")
                return []

            results = await self.vector_store.search_vector(
                query_embedding=query_embedding,
                top_k=top_k,
                doc_ids=doc_ids
            )

            app_logger.info(
                f"-> Vector search hoàn tất. Tìm thấy {len(results)} chunks.")

            return results

        except Exception as e:
            app_logger.error(f"Lỗi trong VectorRetriever: {e}")
            return []
