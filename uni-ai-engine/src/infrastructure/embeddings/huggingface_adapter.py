import asyncio
from typing import List
from sentence_transformers import SentenceTransformer
from infrastructure.embeddings.base import IEmbeddingService
from utils.logger import app_logger
from configs.settings import settings


class HuggingFaceAdapter(IEmbeddingService):
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        app_logger.info(f"Đang tải mô hình Embedding: {model_name}...")
        self.model = SentenceTransformer(model_name)

    def _encode_sync(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    async def embed_text(self, text: str) -> List[float]:
        if not text or not text.strip():
            return []
        try:
            return await asyncio.to_thread(self._encode_sync, text)
        except Exception as e:
            app_logger.error(f"Lỗi khi tạo embedding: {e}")
            return []

    async def embed_query(self, query: str) -> List[float]:
        return await self.embed_text(query)
