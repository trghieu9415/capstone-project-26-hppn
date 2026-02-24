from typing import List

from infrastructure.storage.base import IKeywordStore
from schemas.document import ChildNode


class KeywordRetriever:
    def __init__(self, keyword_store: IKeywordStore):
        self.keyword_store = keyword_store

    def retrieve(self, query: str, top_k: int = 5) -> List[ChildNode]:
        if not query.strip():
            return []

        try:
            results = self.keyword_store.search_keyword(query, top_k=top_k)
            return results
        except Exception as e:
            print(f"[Error] Lỗi trong quá trình Keyword Retrieval: {e}")
            return []
