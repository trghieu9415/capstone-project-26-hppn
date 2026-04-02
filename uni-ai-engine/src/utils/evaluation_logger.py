import logging
from pathlib import Path
import json


class EvaluationLogger:
    def __init__(self, base_dir: str = "logs/evaluate"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.recall_log = self._setup_logger("Recall", "recall_k.txt")
        self.mrr_log = self._setup_logger("MRR", "mrr_k.txt")
        self.faith_log = self._setup_logger("Faithfulness", "faithfulness.txt")
        self.relevance_log = self._setup_logger("AnswerRelevance",
                                                "answer_relevance.txt")
        self.latency_log = self._setup_logger("Latency", "latency.txt")

    def _setup_logger(self, name: str, filename: str) -> logging.Logger:
        logger = logging.getLogger(f"Eval_{name}")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            file_path = self.base_dir / filename
            handler = logging.FileHandler(file_path, mode='a', encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    # =================================================================================
    # CÁC METHOD LOG CHO TỪNG TIÊU CHÍ
    # =================================================================================

    def log_recall(self, query: str, k: int, is_hit: bool, retrieved_docs: int):
        data = {
            "query": query[:50],
            "metric": f"Recall@{k}",
            "is_hit": 1 if is_hit else 0,
            "retrieved_docs": retrieved_docs
        }
        self.recall_log.info(json.dumps(data))

    def log_mrr(self, query: str, k: int, first_relevant_rank: int):
        reciprocal_rank = 1.0 / first_relevant_rank if first_relevant_rank > 0 else 0.0
        data = {
            "query": query[:50],
            "metric": f"MRR@{k}",
            "first_relevant_rank": first_relevant_rank,
            "reciprocal_rank": round(reciprocal_rank, 4)
        }
        self.mrr_log.info(json.dumps(data))

    def log_faithfulness(self, query: str, entailment_score: float):
        data = {
            "query": query[:50],
            "metric": "Faithfulness",
            "score": round(entailment_score, 4)
        }
        self.faith_log.info(json.dumps(data))

    def log_answer_relevance(self, query: str, relevance_score: float):
        data = {
            "query": query[:50],
            "metric": "AnswerRelevance",
            "score": round(relevance_score, 4)
        }
        self.relevance_log.info(json.dumps(data))

    def log_latency(self, query: str, retrieval_time: float, llm_time: float):
        total_time = retrieval_time + llm_time
        data = {
            "query": query[:50],
            "metric": "EndToEndLatency",
            "retrieval_time_sec": round(retrieval_time, 4),
            "llm_time_sec": round(llm_time, 4),
            "total_time_sec": round(total_time, 4)
        }
        self.latency_log.info(json.dumps(data))


eval_logger = EvaluationLogger()
