import datetime
import os
from typing import List, Dict, Any
from uuid import UUID

from sentence_transformers import CrossEncoder

from configs.settings import settings
from schemas.document import ScoredNode
from utils.loggers.app_logger import app_logger


class CrossEncoderReranker:
    def __init__(self, model_name: str = settings.CROSS_ENCODER_MODEL_NAME):
        app_logger.info(f"Đang tải mô hình Cross-Encoder: {model_name}...")
        self.model = CrossEncoder(model_name, max_length=512)
        app_logger.info(f"Mô hình đang chạy trên thiết bị: {self.model.model.device}")
        app_logger.info("Cross-Encoder đã sẵn sàng!")

    def rerank(
        self,
        query: str,
        results: List[ScoredNode],
        top_k: int = settings.CROSS_ENCODER_TOP_K,
    ) -> List[ScoredNode]:

        if not results:
            return []

        unique_nodes: Dict[UUID, Dict[str, Any]] = {}

        for rank, res in enumerate(results, start=1):
            node_id = res.node.id
            if node_id not in unique_nodes:
                unique_nodes[node_id] = {
                    "node": res.node,
                    "cross_score": 0.0,
                    "original_rank": rank
                }

        candidate_items = list(unique_nodes.values())

        sentence_pairs = [[query, item["node"].text_chunk] for item in candidate_items]

        app_logger.debug(
            f"Đang chấm điểm {len(candidate_items)} chunks bằng Cross-Encoder...")

        scores = self.model.predict(sentence_pairs)

        for idx, item in enumerate(candidate_items):
            item["cross_score"] = float(scores[idx])

        candidate_items.sort(key=lambda x: x["cross_score"], reverse=True)
        top_items = candidate_items[:top_k]

        final_nodes = [
            ScoredNode(node=item["node"], score=item["cross_score"])
            for item in top_items
        ]

        app_logger.info(
            f"-> Cross-Encoder Rerank thành công: {len(final_nodes)} kết quả.")
        return final_nodes
