import asyncio
from typing import List
from sentence_transformers import SentenceTransformer
import torch

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

    async def embed_text(self, text: str, is_query: bool = False) -> List[float]:
        if not text or not text.strip():
            return []

        processed_text = f"query: {text}" if is_query else f"passage: {text}"

        try:
            return await asyncio.to_thread(
                lambda: self.model.encode(
                    processed_text,
                    normalize_embeddings=True
                ).tolist()
            )
        except Exception as e:
            app_logger.error(f"Lỗi khi tạo embedding: {e}")
            return []

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        processed_texts = [f"passage: {t}" for t in texts if t.strip()]
        if not processed_texts:
            return []

        try:
            return await asyncio.to_thread(
                lambda: self.model.encode(
                    processed_texts,
                    batch_size=32,
                    normalize_embeddings=True
                ).tolist()
            )
        except Exception as e:
            app_logger.error(f"Lỗi khi tạo batch embedding: {e}")
            return []

    async def embed_query(self, query: str) -> List[float]:
        return await self.embed_text(query, is_query=True)
