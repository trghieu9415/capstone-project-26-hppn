import datetime
import os
from typing import List, Dict, Any
from uuid import UUID

from sentence_transformers import CrossEncoder

from configs.settings import settings
from schemas.document import ScoredNode
from utils.logger import app_logger


def _log_rerank_report(
    initial_results: List[ScoredNode],
    final_items: List[Dict[str, Any]]
):
    try:
        log_dir = "logs/rerank"
        os.makedirs(log_dir, exist_ok=True)
        timestamp_date = datetime.datetime.now().strftime("%Y%m%d")
        file_path = f"{log_dir}/rerank_{timestamp_date}.txt"

        with open(file_path, "a", encoding="utf-8") as f:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            f.write(f"\n\n==================================================\n")
            f.write(f"=== CROSS-ENCODER RERANK REPORT - {current_time} ===\n")
            f.write(f"==================================================\n\n")

            f.write(
                f"--- [1] INITIAL HYBRID RESULTS (Total: {len(initial_results)}) ---\n")
            for i, r in enumerate(initial_results[:10]):
                short_text = r.node.text_chunk[:100].replace("\n", " ")
                f.write(
                    f"Input Rank {i + 1} | Base Score={r.score:.5f}: ID={r.node.id} | Content:{short_text}...\n")

            f.write(
                f"\n--- [2] FINAL CROSS-ENCODER RESULTS (TOP {len(final_items)}) ---\n")
            for i, item in enumerate(final_items):
                short_text = item['node'].text_chunk[:100].replace("\n", " ")
                f.write(
                    f"Final Rank {i + 1} | CE Score={item['cross_score']:.5f} | Original Rank={item['original_rank']} | Content={short_text}...\n")

    except Exception as e:
        app_logger.warning(f"Lỗi ghi log rerank: {e}")


class CrossEncoderReranker:
    def __init__(self, model_name: str = settings.CROSS_ENCODER_MODEL_NAME):
        app_logger.info(f"Đang tải mô hình Cross-Encoder: {model_name}...")
        self.model = CrossEncoder(model_name, max_length=512)
        app_logger.info("Cross-Encoder đã sẵn sàng!")

    def rerank(
        self,
        query: str,
        results: List[ScoredNode],
        top_k: int = 6
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

        _log_rerank_report(results, top_items)

        final_nodes = [
            ScoredNode(node=item["node"], score=item["cross_score"])
            for item in top_items
        ]

        app_logger.info(
            f"-> Cross-Encoder Rerank thành công: {len(final_nodes)} kết quả.")
        return final_nodes
