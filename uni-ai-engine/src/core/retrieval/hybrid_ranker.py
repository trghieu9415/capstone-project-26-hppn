import datetime
import os
from typing import List, Dict, Any
from uuid import UUID

from sentence_transformers import CrossEncoder
from schemas.document import ScoredNode
from utils.logger import app_logger


def _log_rerank_report(
    v_res: List[ScoredNode], k_res: List[ScoredNode],
    final_items: List[Dict[str, Any]]):
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

            f.write(f"--- [1] TOP VECTOR RESULTS ({len(v_res)}) ---\n")
            for i, r in enumerate(v_res[:5]):
                short_text = r.node.text_chunk[:100].replace("\n", " ")
                f.write(f"Rank {i + 1}: ID={r.node.id} | Content={short_text}...\n")

            f.write(f"\n--- [2] TOP KEYWORD RESULTS ({len(k_res)}) ---\n")
            for i, r in enumerate(k_res[:5]):
                short_text = r.node.text_chunk[:100].replace("\n", " ")
                f.write(f"Rank {i + 1}: ID={r.node.id} | Content={short_text}...\n")

            f.write(
                f"\n--- [3] FINAL CROSS-ENCODER RESULTS (TOP {len(final_items)}) ---\n")
            for i, item in enumerate(final_items):
                short_text = item['node'].text_chunk[:100].replace("\n", " ")
                f.write(
                    f"CE Rank {i + 1}: Score={item['cross_score']:.5f} | Sources={item['sources']} | Content={short_text}...\n")

    except Exception as e:
        app_logger.warning(f"Lỗi ghi log rerank: {e}")


class HybridRanker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        app_logger.info(f"Đang tải mô hình Cross-Encoder: {model_name}...")
        self.model = CrossEncoder(model_name, max_length=512)
        app_logger.info("Cross-Encoder đã sẵn sàng!")

    def rerank(
        self,
        query: str,
        vector_results: List[ScoredNode],
        keyword_results: List[ScoredNode],
        top_k: int = 6
    ) -> List[ScoredNode]:

        unique_nodes: Dict[UUID, Dict[str, Any]] = {}

        def _add_to_candidates(results: List[ScoredNode], source_name: str):
            for rank, res in enumerate(results, start=1):
                node_id = res.node.id
                if node_id not in unique_nodes:
                    unique_nodes[node_id] = {
                        "node": res.node,
                        "sources": [],
                        "cross_score": 0.0
                    }
                unique_nodes[node_id]["sources"].append(f"{source_name}(Rank:{rank})")

        _add_to_candidates(vector_results, "Vector")
        _add_to_candidates(keyword_results, "Keyword")

        candidate_items = list(unique_nodes.values())
        if not candidate_items:
            return []

        sentence_pairs = [[query, item["node"].text_chunk] for item in candidate_items]

        app_logger.debug(
            f"Đang chấm điểm {len(candidate_items)} chunks bằng Cross-Encoder...")
        scores = self.model.predict(sentence_pairs)

        for idx, item in enumerate(candidate_items):
            item["cross_score"] = float(scores[idx])

        candidate_items.sort(key=lambda x: x["cross_score"], reverse=True)
        top_items = candidate_items[:top_k]

        _log_rerank_report(vector_results, keyword_results, top_items)

        final_nodes = [
            ScoredNode(node=item["node"], score=item["cross_score"])
            for item in top_items
        ]

        app_logger.info(
            f"-> Cross-Encoder Rerank thành công: {len(final_nodes)} kết quả.")
        return final_nodes
