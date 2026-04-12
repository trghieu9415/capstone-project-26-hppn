from abc import ABC, abstractmethod
from typing import List, Any, Dict

from schemas.document import ParentNode, ChildNode


class IEmbeddingService(ABC):
    @abstractmethod
    async def embed_text(self, text: str, is_query: bool = False) -> List[float]:
        pass

    @abstractmethod
    async def embed_query(self, query: str) -> List[float]:
        pass

    # Bổ sung hàm xử lý hàng loạt
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        pass

    async def chunk_and_embed(
        self,
        parent_node: ParentNode,
        metadata: Dict[str, Any] = None
    ) -> List[ChildNode]:
        pass
