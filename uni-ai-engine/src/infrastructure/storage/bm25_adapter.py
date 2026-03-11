import os
import pickle
import asyncio
from typing import List, Optional
from uuid import UUID
from rank_bm25 import BM25Okapi
from pyvi import ViTokenizer  # Import thư viện cắt từ tiếng Việt

from infrastructure.storage.base import IKeywordStore
from schemas.document import ChildNode, ScoredNode
from utils.logger import app_logger


class BM25KeywordStore(IKeywordStore):
    def __init__(self, persist_dir: str = "../data/keyword_db"):
        self.persist_dir = persist_dir
        self.index_path = os.path.join(self.persist_dir, "bm25_nodes.pkl")

        self.nodes: List[ChildNode] = []
        self.bm25: Optional[BM25Okapi] = None
        self._lock = asyncio.Lock()

        os.makedirs(self.persist_dir, exist_ok=True)
        self._load_index_sync()

    # INTERNAL METHODS
    def _tokenize(self, text: str) -> List[str]:
        tokenized_text = ViTokenizer.tokenize(text)
        return tokenized_text.lower().split()

    def _load_index_sync(self):
        if os.path.exists(self.index_path):
            with open(self.index_path, "rb") as f:
                self.nodes = pickle.load(f)
            self._rebuild_bm25()

    def _save_index_sync(self):
        with open(self.index_path, "wb") as f:
            pickle.dump(self.nodes, f)

    def _rebuild_bm25(self):
        if self.nodes:
            corpus = [self._tokenize(node.text_chunk) for node in self.nodes]
            self.bm25 = BM25Okapi(corpus)
        else:
            self.bm25 = None

    # INTERFACE IMPLEMENTATION
    async def save_children(self, nodes: List[ChildNode]) -> bool:
        if not nodes:
            return True

        async with self._lock:
            try:
                await asyncio.to_thread(self._save_and_rebuild, nodes, is_append=True)
                return True
            except Exception as e:
                print(f"BM25 Save Error: {e}")
                return False

    async def delete_children_by_parent_ids(self, parent_ids: List[UUID]) -> bool:
        if not parent_ids:
            return True

        async with self._lock:
            try:
                await asyncio.to_thread(self._delete_and_rebuild, parent_ids)
                return True
            except Exception as e:
                print(f"BM25 Delete Error: {e}")
                return False

    async def search_keyword(
        self,
        query: str,
        top_k: int = 5,
        doc_ids: Optional[List[UUID]] = None,
    ) -> List[ScoredNode]:

        if not self.bm25 or not self.nodes:
            return []

        def _search():
            tokenized_query = self._tokenize(query)
            app_logger.info(f"[BM25] Tokenized Query: {tokenized_query}")

            scores = self.bm25.get_scores(tokenized_query)
            scored_nodes = list(zip(self.nodes, scores))

            if doc_ids is not None and len(doc_ids) > 0:
                doc_ids_set = set(doc_ids)
                scored_nodes = [
                    (node, score) for node, score in scored_nodes
                    if node.parent_id in doc_ids_set
                       or node.metadata.get("doc_id") in doc_ids_set
                ]

            scored_nodes = [x for x in scored_nodes if x[1] > 0]
            scored_nodes.sort(key=lambda x: x[1], reverse=True)

            from schemas.document import ScoredNode
            return [
                ScoredNode(node=node, score=score) for node,
                score in scored_nodes[:top_k]
            ]

        return await asyncio.to_thread(_search)

    # THREAD WORKERS
    def _save_and_rebuild(self, new_nodes: List[ChildNode], is_append: bool = True):
        if is_append:
            self.nodes.extend(new_nodes)
        else:
            self.nodes = new_nodes

        self._save_index_sync()
        self._rebuild_bm25()

    def _delete_and_rebuild(self, parent_ids: List[UUID]):
        self.nodes = [node for node in self.nodes if node.parent_id not in parent_ids]
        self._save_index_sync()
        self._rebuild_bm25()
