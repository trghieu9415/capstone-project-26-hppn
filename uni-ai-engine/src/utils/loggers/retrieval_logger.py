import os
import logging
import functools
from datetime import datetime
from typing import List, Set

from schemas.document import ChildNode, ScoredNode


def ensure_log_file(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.logger.hasHandlers() or func.__name__ == "log_vector_search":
            self._init_new_log_file()
        return func(self, *args, **kwargs)

    return wrapper


class RetrievalLogger:
    def __init__(self, log_dir: str = "logs/retrieval", file_prefix: str = "retrieval"):
        self.log_dir = log_dir
        self.file_prefix = file_prefix
        self.logger = logging.getLogger("RetrievalLogger")
        self.logger.setLevel(logging.INFO)

        self._latest_vector_ids: Set[str] = set()
        self._latest_keyword_ids: Set[str] = set()

    def _init_new_log_file(self):
        if self.logger.hasHandlers():
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)

        os.makedirs(self.log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"{self.file_prefix}_{timestamp}.log")

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    @staticmethod
    def _get_node_id(node: ChildNode) -> str:
        return f"{node.parent_id}[{node.chunk_index}]"

    def _format_node(self, stage_type: str, scored_node: ScoredNode,
                     source: str = "") -> str:
        node_id = self._get_node_id(scored_node.node)
        short_text = scored_node.node.text_chunk[:400].replace('\n', ' ')
        source_str = f" | Source: {source}" if source else ""
        return f"[{stage_type}] Score: {scored_node.score:.4f} | ID: {node_id}{source_str} | Text: {short_text}..."

    def _log_stage_core(self, stage_name: str, query: str, results: List[ScoredNode]):
        self.logger.info(f"--- {stage_name.upper()} SEARCH ---")
        self.logger.info(f"Query: '{query}'")
        self.logger.info(f"Retrieved: {len(results)} nodes")
        for res in results:
            self.logger.info(self._format_node(stage_name, res))
        self.logger.info("-" * 50)

    @ensure_log_file
    def log_vector_search(self, query: str, results: List[ScoredNode]):
        self._latest_vector_ids = {self._get_node_id(res.node) for res in results}
        self._log_stage_core("Vector", query, results)

    @ensure_log_file
    def log_keyword_search(self, query: str, results: List[ScoredNode]):
        self._latest_keyword_ids = {self._get_node_id(res.node) for res in results}
        self._log_stage_core("Keyword", query, results)

    @ensure_log_file
    def log_hybrid_search(self, query: str, results: List[ScoredNode]):
        self.logger.info(f"--- HYBRID SEARCH (Alpha Blending) ---")
        self.logger.info(f"Query: '{query}'")
        self.logger.info(f"Retrieved: {len(results)} nodes")

        for res in results:
            node_id = self._get_node_id(res.node)
            is_vector = node_id in self._latest_vector_ids
            is_keyword = node_id in self._latest_keyword_ids

            source = "Both" if (is_vector and is_keyword) else \
                "Vector" if is_vector else \
                    "Keyword" if is_keyword else "Unknown"

            self.logger.info(self._format_node("Hybrid", res, source=source))

        self.logger.info("-" * 50)
        self._latest_vector_ids.clear()
        self._latest_keyword_ids.clear()

    @ensure_log_file
    def log_cross_encoder(self, query: str, results: List[ScoredNode]):
        self._log_stage_core("Cross", query, results)


retrieval_logger = RetrievalLogger()
