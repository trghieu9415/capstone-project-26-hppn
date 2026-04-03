import datetime
import os
from typing import List, Dict, Any
from uuid import UUID

from configs.settings import settings
from schemas.document import ScoredNode
from utils.loggers.app_logger import app_logger
from utils.loggers.retrieval_logger import retrieval_logger


class HybridRanker:
    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha
        app_logger.info(
            f"Đã khởi tạo HybridRanker bằng thuật toán Alpha Blending (Alpha={self.alpha})")

    @staticmethod
    def _normalize_scores(results: List[ScoredNode]) -> Dict[UUID, float]:
        if not results:
            return {}

        scores = [r.score for r in results]
        min_score = min(scores)
        max_score = max(scores)

        normalized_map = {}
        for r in results:
            if max_score == min_score:
                norm_score = 1.0
            else:
                norm_score = (r.score - min_score) / (max_score - min_score)
            normalized_map[r.node.id] = norm_score

        return normalized_map

    def rerank(
        self,
        vector_results: List[ScoredNode],
        keyword_results: List[ScoredNode],
        top_k: int = settings.ALPHA_BLENDING_TOP_K
    ) -> List[ScoredNode]:

        norm_vector = self._normalize_scores(vector_results)
        norm_keyword = self._normalize_scores(keyword_results)

        final_map: Dict[UUID, Dict[str, Any]] = {}

        def _add_nodes(results: List[ScoredNode], source_name: str):
            for rank, r in enumerate(results, start=1):
                if r.node.id not in final_map:
                    final_map[r.node.id] = {
                        "node": r.node,
                        "v_score": 0.0,
                        "k_score": 0.0,
                        "sources": []
                    }
                final_map[r.node.id]["sources"].append(f"{source_name}(Rank:{rank})")

        _add_nodes(vector_results, "Vector")
        _add_nodes(keyword_results, "Keyword")

        for node_id, data in final_map.items():
            v_s = norm_vector.get(node_id, 0.0)
            k_s = norm_keyword.get(node_id, 0.0)

            data["v_score"] = v_s
            data["k_score"] = k_s
            data["final_score"] = (self.alpha * v_s) + ((1.0 - self.alpha) * k_s)

        sorted_items = sorted(
            final_map.values(),
            key=lambda x: x["final_score"],
            reverse=True
        )

        top_items = sorted_items[:top_k]
        final_nodes = [
            ScoredNode(node=item["node"], score=item["final_score"])
            for item in top_items
        ]

        app_logger.info(
            f"-> Rerank (Alpha Blending) thành công: {len(final_nodes)} kết quả.")
        return final_nodes
