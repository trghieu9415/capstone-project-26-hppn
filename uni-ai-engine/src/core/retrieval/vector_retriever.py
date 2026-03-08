from typing import List, Optional

from infrastructure.embeddings.base import IEmbeddingService
from infrastructure.storage.base import IVectorStore
from schemas.document import ChildNode
from schemas.request import DocumentFilter
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
        self, query: str, top_k: int = 5, filters: Optional[DocumentFilter] = None
    ) -> List[ChildNode]:
        if not query.strip():
            return []

        try:
            query_embedding = await self.embedding_service.embed_query(query)
            results = await self.vector_store.search_vector(
                query_embedding, top_k=top_k, filters=filters
            )
            return results
        except Exception as e:
            app_logger.error(f"Lỗi trong quá trình Vector Retrieval: {e}")
            return []
