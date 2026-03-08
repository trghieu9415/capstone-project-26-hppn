from abc import ABC, abstractmethod
from typing import List, Optional
from schemas.document import ChildNode, ParentNode
from schemas.request import DocumentFilter


class IDocumentStore(ABC):
    @abstractmethod
    async def save_parents(self, nodes: List[ParentNode]) -> bool:
        pass

    @abstractmethod
    async def get_parents_by_ids(self, parent_ids: List[str]) -> List[ParentNode]:
        pass


class IVectorStore(ABC):
    @abstractmethod
    async def save_children(self, nodes: List[ChildNode]) -> bool:
        pass

    @abstractmethod
    async def search_vector(
        self, query_embedding: List[float], top_k: int = 5,
        filters: Optional[DocumentFilter] = None
    ) -> List[ChildNode]:
        pass


class IKeywordStore(ABC):
    @abstractmethod
    async def save_children(self, nodes: List[ChildNode]) -> bool:
        pass

    # Sửa dòng này
    @abstractmethod
    async def search_keyword(
        self, query: str, top_k: int = 5,
        filters: Optional[DocumentFilter] = None
    ) -> List[ChildNode]:
        pass
