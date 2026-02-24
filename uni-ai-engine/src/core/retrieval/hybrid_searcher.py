from typing import List, Dict
from core.retrieval.vector_retriever import VectorRetriever
from core.retrieval.keyword_retriever import KeywordRetriever
from schemas.document import ChildNode


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

    def search(self, query: str, top_k: int = 5) -> List[ChildNode]:
        if not query.strip():
            return []

        fetch_k = top_k * 2

        vector_results = self.vector_retriever.retrieve(query, top_k=fetch_k)
        keyword_results = self.keyword_retriever.retrieve(query, top_k=fetch_k)

        rrf_scores: Dict[str, float] = {}
        node_map: Dict[str, ChildNode] = {}

        for rank, node in enumerate(vector_results, start=1):
            if node.id not in rrf_scores:
                rrf_scores[node.id] = 0.0
                node_map[node.id] = node

            rrf_scores[node.id] += 1.0 / (self.rrf_k + rank)

        for rank, node in enumerate(keyword_results, start=1):
            if node.id not in rrf_scores:
                rrf_scores[node.id] = 0.0
                node_map[node.id] = node

            rrf_scores[node.id] += 1.0 / (self.rrf_k + rank)

        sorted_items = sorted(
            rrf_scores.items(), key=lambda item: item[1], reverse=True
        )

        final_results = []
        for node_id, rrf_score in sorted_items[:top_k]:
            node = node_map[node_id]

            node.metadata["rrf_score"] = rrf_score
            final_results.append(node)

        return final_results
