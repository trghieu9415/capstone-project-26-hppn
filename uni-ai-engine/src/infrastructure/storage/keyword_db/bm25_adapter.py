import os
import pickle
from typing import List
from rank_bm25 import BM25Okapi

from infrastructure.storage.base import IKeywordStore
from schemas.document import ChildNode


class BM25Adapter(IKeywordStore):
    def __init__(self, persist_dir: str = "./data/bm25_index"):
        self.persist_dir = persist_dir
        self.index_file = os.path.join(persist_dir, "bm25_data.pkl")
        self.nodes: List[ChildNode] = []
        self.bm25: BM25Okapi = None

        os.makedirs(persist_dir, exist_ok=True)
        self._load_index()

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        return text.lower().split()

    def _load_index(self):
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "rb") as f:
                    data = pickle.load(f)
                    self.nodes = data.get("nodes", [])
                    corpus = data.get("corpus", [])
                    if corpus:
                        self.bm25 = BM25Okapi(corpus)
            except Exception as e:
                print(f"[Error] Lỗi đọc BM25 Index: {e}")

    def _save_index(self, corpus: List[List[str]]):
        try:
            with open(self.index_file, "wb") as f:
                pickle.dump({"nodes": self.nodes, "corpus": corpus}, f)
        except Exception as e:
            print(f"[Error] Lỗi lưu BM25 Index: {e}")

    def save_children(self, nodes: List[ChildNode]) -> bool:
        if not nodes:
            return True

        try:
            self.nodes.extend(nodes)

            corpus = [self._tokenize(node.text_chunk) for node in self.nodes]
            self.bm25 = BM25Okapi(corpus)

            self._save_index(corpus)
            return True
        except Exception as e:
            print(f"[Error] Lỗi khi lưu vào BM25: {e}")
            return False

    def search_keyword(self, query: str, top_k: int = 5) -> List[ChildNode]:
        if not self.bm25 or not self.nodes:
            return []

        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        top_n_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True
        )[:top_k]

        results = []
        for idx in top_n_indices:
            if scores[idx] > 0:
                node = self.nodes[idx]
                node.metadata["bm25_score"] = scores[idx]
                results.append(node)

        return results
