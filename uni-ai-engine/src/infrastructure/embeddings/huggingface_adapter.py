import asyncio
from typing import List
from sentence_transformers import SentenceTransformer
import torch  # Bổ sung để check thiết bị

from infrastructure.embeddings.base import IEmbeddingService
from utils.logger import app_logger
from configs.settings import settings


class HuggingFaceAdapter(IEmbeddingService):
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        device = "cuda" if torch.cuda.is_available() \
            else "mps" if torch.backends.mps.is_available() \
            else "cpu"

        app_logger.info(
            f"Đang tải mô hình Embedding: {model_name} trên {device.upper()}...")
        self.model = SentenceTransformer(model_name, device=device)

    def _encode_sync(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def _encode_batch_sync(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()

    async def embed_text(self, text: str) -> List[float]:
        if not text or not text.strip():
            return []
        try:
            return await asyncio.to_thread(self._encode_sync, text)
        except Exception as e:
            app_logger.error(f"Lỗi khi tạo embedding: {e}")
            return []

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            return []
        try:
            return await asyncio.to_thread(self._encode_batch_sync, valid_texts)
        except Exception as e:
            app_logger.error(f"Lỗi khi tạo batch embedding: {e}")
            return []

    async def embed_query(self, query: str) -> List[float]:
        """
        return await self.embed_text(f"query: {query}")
        """
        return await self.embed_text(query)
