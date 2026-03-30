import datetime
import os
from typing import List, Dict, Any
from uuid import UUID
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
            f.write(f"=== ALPHA BLENDING RERANK REPORT - {current_time} ===\n")
            f.write(f"==================================================\n\n")

            f.write(f"--- [1] TOP VECTOR RESULTS ({len(v_res)}) ---\n")
            for i, r in enumerate(v_res[:5]):
                short_text = r.node.text_chunk[:100].replace("\n", " ")
                f.write(
                    f"Score={r.score:.5f}: ID={r.node.metadata["file_name"]} | Content:{short_text}...\n")

            f.write(f"\n--- [2] TOP KEYWORD RESULTS ({len(k_res)}) ---\n")
            for i, r in enumerate(k_res[:5]):
                short_text = r.node.text_chunk[:100].replace("\n", " ")
                f.write(
                    f"Score={r.score:.5f}: ID={r.node.metadata["file_name"]} | Content={short_text}...\n")

            f.write(
                f"\n--- [3] FINAL ALPHA BLENDING RESULTS (TOP {len(final_items)}) ---\n")
            for i, item in enumerate(final_items):
                short_text = item['node'].text_chunk[:100].replace("\n", " ")
                f.write(
                    f"Rank {i + 1} | Final={item['final_score']:.5f} (V:{item['v_score']:.3f}, K:{item['k_score']:.3f}) | Sources={item['sources']} | Content={short_text}...\n")

    except Exception as e:
        app_logger.warning(f"Lỗi ghi log rerank: {e}")


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
        top_k: int = 10
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

        _log_rerank_report(vector_results, keyword_results, top_items)

        app_logger.info(
            f"-> Rerank (Alpha Blending) thành công: {len(final_nodes)} kết quả.")
        return final_nodes
