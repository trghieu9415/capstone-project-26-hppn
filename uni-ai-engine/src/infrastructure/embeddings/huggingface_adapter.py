from typing import List
from sentence_transformers import SentenceTransformer

from core.retrieval.vector_retriever import IEmbeddingService


class HuggingFaceAdapter(IEmbeddingService):
    def __init__(self, model_name: str = "keepitreal/vietnamese-sbert"):
        print(
            f"[Info] Đang tải mô hình Embedding: {model_name} (Sẽ hơi lâu ở lần đầu tiên)..."
        )
        self.model = SentenceTransformer(model_name)
        print("[Info] Đã tải mô hình Embedding thành công!")

    def embed_text(self, text: str) -> List[float]:
        if not text or not text.strip():
            return []

        try:
            vector = self.model.encode(text)
            return vector.tolist()
        except Exception as e:
            print(f"[Error] Lỗi khi tạo embedding cho text: {e}")
            return []

    def embed_query(self, query: str) -> List[float]:
        if not query or not query.strip():
            return []

        try:
            vector = self.model.encode(query)
            return vector.tolist()
        except Exception as e:
            print(f"[Error] Lỗi khi tạo embedding cho query: {e}")
            return []
