import requests
from typing import List

from core.retrieval.vector_retriever import IEmbeddingService


class HuggingFaceApiAdapter(IEmbeddingService):
    def __init__(self, api_key: str, model_name: str = "keepitreal/vietnamese-sbert"):
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_name}"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def _call_api(self, text: str) -> List[float]:
        try:
            response = requests.post(
                self.api_url, headers=self.headers, json={"inputs": text}
            )
            response.raise_for_status()

            return response.json()
        except Exception as e:
            print(f"[Error] Lỗi gọi Hugging Face API: {e}")
            return []

    def embed_text(self, text: str) -> List[float]:
        if not text.strip():
            return []
        return self._call_api(text)

    def embed_query(self, query: str) -> List[float]:
        if not query.strip():
            return []
        return self._call_api(query)
