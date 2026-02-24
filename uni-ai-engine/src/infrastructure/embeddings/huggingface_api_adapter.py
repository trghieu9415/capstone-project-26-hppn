import httpx  # DÙNG HTTPX THAY CHO REQUESTS
from typing import List
from infrastructure.embeddings.base import IEmbeddingService
from utils.logger import app_logger


class HuggingFaceApiAdapter(IEmbeddingService):
    def __init__(self, api_key: str, model_name: str = "keepitreal/vietnamese-sbert"):
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    async def _call_api(self, text: str) -> List[float]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url, headers=self.headers, json={"inputs": text}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            app_logger.error(f"Lỗi gọi Hugging Face API: {e}")
            return []

    async def embed_text(self, text: str) -> List[float]:
        if not text.strip():
            return []
        return await self._call_api(text)

    async def embed_query(self, query: str) -> List[float]:
        if not query.strip():
            return []
        return await self._call_api(query)
