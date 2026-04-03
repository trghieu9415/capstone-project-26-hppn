import os
import logging
from datetime import datetime
from typing import List, Dict

from schemas.document import ChildNode, ScoredNode


class RetrievalLogger:
    def __init__(self, log_dir: str = "logs/retrieval", file_prefix: str = "retrieval"):
        os.makedirs(log_dir, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d%H%M%S")
        log_file = os.path.join(log_dir, f"{file_prefix}_{date_str}.log")

        self.logger = logging.getLogger("RetrievalLogger")
        self.logger.setLevel(logging.INFO)

        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self._latest_vector_ids = set()
        self._latest_keyword_ids = set()

    @staticmethod
    def _get_node_id(node: ChildNode) -> str:
        return f"{node.parent_id}[{node.chunk_index}]"

    def _format_node(
        self, stage_type: str, scored_node: ScoredNode,
        source: str = ""
    ) -> str:
        node_id = self._get_node_id(scored_node.node)
        short_text = scored_node.node.text_chunk[:100].replace('\n', ' ')
        source_str = f" | Source: {source}" if source else ""
        return f"[{stage_type}] Score: {scored_node.score:.4f} | ID: {node_id}{source_str} | Text: {short_text}..."

    def _log_stage(self, stage_name: str, query: str, results: List[ScoredNode]):
        self.logger.info(f"--- {stage_name.upper()} SEARCH ---")
        self.logger.info(f"Query: '{query}'")
        self.logger.info(f"Retrieved: {len(results)} nodes")
        for res in results:
            self.logger.info(self._format_node(stage_name, res))
        self.logger.info("-" * 50)

    def log_vector_search(self, query: str, results: List[ScoredNode]):
        self._latest_vector_ids = {self._get_node_id(res.node) for res in results}
        self._log_stage("Vector", query, results)

    def log_keyword_search(self, query: str, results: List[ScoredNode]):
        self._latest_keyword_ids = {self._get_node_id(res.node) for res in results}
        self._log_stage("Keyword", query, results)

    def log_hybrid_search(self, query: str, results: List[ScoredNode]):
        self.logger.info(f"--- HYBRID SEARCH (Alpha Blending) ---")
        self.logger.info(f"Query: '{query}'")
        self.logger.info(f"Retrieved: {len(results)} nodes")

        for res in results:
            node_id = self._get_node_id(res.node)

            is_vector = node_id in self._latest_vector_ids
            is_keyword = node_id in self._latest_keyword_ids

            if is_vector and is_keyword:
                source = "Both"
            elif is_vector:
                source = "Vector"
            elif is_keyword:
                source = "Keyword"
            else:
                source = "Unknown"

            self.logger.info(self._format_node("Hybrid", res, source=source))

        self.logger.info("-" * 50)
        self._latest_vector_ids.clear()
        self._latest_keyword_ids.clear()

    def log_cross_encoder(self, query: str, results: List[ScoredNode]):
        self._log_stage("Cross", query, results)


retrieval_logger = RetrievalLogger()
