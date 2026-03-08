import asyncio
from typing import List, Dict, Optional

from core.retrieval.vector_retriever import VectorRetriever
from core.retrieval.keyword_retriever import KeywordRetriever
from schemas.document import ChildNode
from schemas.request import DocumentFilter
from utils.logger import app_logger


class HybridSearcher:
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        keyword_retriever: KeywordRetriever,
        rrf_k: int = 60,
    ):
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.rrf_k = rrf_k

    async def search(
        self, query: str, top_k: int = 5, filters: Optional[DocumentFilter] = None
    ) -> List[ChildNode]:
        if not query.strip():
            return []

        fetch_k = top_k * 2

        app_logger.debug(f"Bắt đầu Hybrid Search: '{query}' với filters: {filters}")

        vector_results, keyword_results = await asyncio.gather(
            self.vector_retriever.retrieve(query, top_k=fetch_k, filters=filters),
            self.keyword_retriever.retrieve(query, top_k=fetch_k, filters=filters),
        )

        rrf_scores: Dict[str, float] = {}
        node_map: Dict[str, ChildNode] = {}

        for rank, node in enumerate(vector_results, start=1):
            node_id = str(node.id)
            if node_id not in rrf_scores:
                rrf_scores[node_id] = 0.0
                node_map[node_id] = node.model_copy(deep=True)
            rrf_scores[node_id] += 1.0 / (self.rrf_k + rank)

        for rank, node in enumerate(keyword_results, start=1):
            node_id = str(node.id)
            if node_id not in rrf_scores:
                rrf_scores[node_id] = 0.0
                node_map[node_id] = node.model_copy(deep=True)
            rrf_scores[node_id] += 1.0 / (self.rrf_k + rank)

        sorted_items = sorted(
            rrf_scores.items(), key=lambda item: item[1], reverse=True
        )

        final_results = []
        for node_id, rrf_score in sorted_items[:top_k]:
            node = node_map[node_id]
            node.metadata.extra_info["rrf_score"] = float(rrf_score)
            final_results.append(node)

        app_logger.info(
            f"Hybrid Search hoàn tất, trả về {len(final_results)} chunks tốt nhất."
        )
        return final_results
