from typing import List, Dict, Any
from uuid import UUID

from schemas.document import ScoredNode
from utils.logger import app_logger


class HybridRanker:
    def __init__(self, k_constant: int = 60):
        self.k = k_constant

    def _update_rrf_scores(
        self,
        results: List[ScoredNode],
        rrf_map: Dict[UUID, Dict[str, Any]]
    ):
        for rank, scored_node in enumerate(results, start=1):
            node_id = scored_node.node.id

            if node_id not in rrf_map:
                rrf_map[node_id] = {
                    "node": scored_node.node,
                    "rrf_score": 0.0
                }

            rrf_map[node_id]["rrf_score"] += 1.0 / (self.k + rank + 1)

    def rerank(
        self,
        vector_results: List[ScoredNode],
        keyword_results: List[ScoredNode],
        top_k: int = 5
    ) -> List[ScoredNode]:
        rrf_map: Dict[UUID, Dict[str, Any]] = {}
        self._update_rrf_scores(vector_results, rrf_map)
        self._update_rrf_scores(keyword_results, rrf_map)

        sorted_items = sorted(
            rrf_map.values(),
            key=lambda x: x["rrf_score"],
            reverse=True
        )

        final_nodes = [
            ScoredNode(node=item["node"], score=item["rrf_score"])
            for item in sorted_items[:top_k]
        ]

        app_logger.info(f"-> Hybrid Rerank thành công: {len(final_nodes)} kết quả.")
        return final_nodes
