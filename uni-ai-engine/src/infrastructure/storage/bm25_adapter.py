import os
import pickle
import asyncio
from typing import List, Optional
from rank_bm25 import BM25Okapi

from infrastructure.storage.base import IKeywordStore
from schemas.document import ChildNode
from schemas.request import DocumentFilter
from utils.logger import app_logger


class BM25Adapter(IKeywordStore):
    def __init__(self, persist_dir: str = "./data/bm25_index"):
        self.persist_dir = persist_dir
        self.index_file = os.path.join(persist_dir, "bm25_data.pkl")
        self.nodes: List[ChildNode] = []
        self.bm25: Optional[BM25Okapi] = None

        self._lock = asyncio.Lock()

        os.makedirs(persist_dir, exist_ok=True)
        self._load_index_sync()

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        if not text:
            return []
        return text.lower().split()

    def _load_index_sync(self):
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "rb") as f:
                    data = pickle.load(f)
                    self.nodes = data.get("nodes", [])
                    corpus = data.get("corpus", [])
                    if corpus:
                        self.bm25 = BM25Okapi(corpus)
                app_logger.info(f"Đã load BM25 index với {len(self.nodes)} nodes.")
            except Exception as e:
                app_logger.error(f"Lỗi đọc BM25 Index: {e}")

    def _save_index_sync(self, corpus: List[List[str]]):
        try:
            with open(self.index_file, "wb") as f:
                pickle.dump({"nodes": self.nodes, "corpus": corpus}, f)
            app_logger.info("Đã lưu BM25 Index xuống ổ cứng.")
        except Exception as e:
            app_logger.error(f"Lỗi lưu BM25 Index: {e}")

    @staticmethod
    def _build_bm25_sync(corpus: List[List[str]]):
        return BM25Okapi(corpus)

    async def save_children(self, nodes: List[ChildNode]) -> bool:
        if not nodes:
            return True

        async with self._lock:
            try:
                self.nodes.extend(nodes)
                corpus = await asyncio.to_thread(
                    lambda: [self._tokenize(node.text_chunk) for node in self.nodes]
                )
                self.bm25 = await asyncio.to_thread(self._build_bm25_sync, corpus)
                await asyncio.to_thread(self._save_index_sync, corpus)
                return True
            except Exception as e:
                app_logger.error(f"Lỗi khi lưu vào BM25: {e}")
                return False

    async def search_keyword(
        self, query: str, top_k: int = 5, filters: Optional[DocumentFilter] = None
    ) -> List[ChildNode]:
        if not self.bm25 or not self.nodes:
            return []

        try:
            tokenized_query = self._tokenize(query)
            scores = await asyncio.to_thread(self.bm25.get_scores, tokenized_query)

            filtered_indices = []
            for idx, node in enumerate(self.nodes):
                meta = node.metadata
                if filters:
                    if meta.user_id != filters.user_id:
                        continue
                    if filters.folder_id and meta.folder_id != filters.folder_id:
                        continue
                    if filters.document_id and meta.document_id != filters.document_id:
                        continue
                    if filters.tags and not any(
                        tag in meta.tags for tag in filters.tags):
                        continue

                if scores[idx] > 0:
                    filtered_indices.append(idx)

            top_n_indices = sorted(
                filtered_indices, key=lambda i: scores[i], reverse=True
            )[:top_k]

            results = []
            for idx in top_n_indices:
                node = self.nodes[idx].model_copy(deep=True)
                node.metadata.extra_info["bm25_score"] = float(scores[idx])
                results.append(node)

            return results
        except Exception as e:
            app_logger.error(f"Lỗi khi tìm kiếm BM25: {e}")
            return []
