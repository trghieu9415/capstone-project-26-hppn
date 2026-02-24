from typing import List

from infrastructure.embeddings.base import IEmbeddingService
from infrastructure.storage.base import IVectorStore
from schemas.document import ChildNode


class VectorRetriever:
    def __init__(
        self, vector_store: IVectorStore, embedding_service: IEmbeddingService
    ):

        self.vector_store = vector_store
        self.embedding_service = embedding_service

    def retrieve(self, query: str, top_k: int = 5) -> List[ChildNode]:
        if not query.strip():
            return []

        try:
            query_embedding = self.embedding_service.embed_query(query)
            results = self.vector_store.search_vector(query_embedding, top_k=top_k)
            return results
        except Exception as e:
            print(f"[Error] Lỗi trong quá trình Vector Retrieval: {e}")
            return []
