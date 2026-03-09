from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from schemas.document import ChildNode, ParentNode, ScoredNode


class IDocumentStore(ABC):
    @abstractmethod
    async def save_parents(self, nodes: List[ParentNode]) -> bool:
        pass

    @abstractmethod
    async def get_parents_by_ids(self, parent_ids: List[UUID]) -> List[ParentNode]:
        pass

    @abstractmethod
    async def delete_parents(self, parent_ids: List[UUID]) -> bool:
        pass


class IVectorStore(ABC):
    @abstractmethod
    async def save_children(self, nodes: List[ChildNode]) -> bool:
        pass

    @abstractmethod
    async def search_vector(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        doc_ids: Optional[List[UUID]] = None,
    ) -> List[ScoredNode]:
        pass

    @abstractmethod
    async def delete_children_by_parent_ids(self, parent_ids: List[UUID]) -> bool:
        pass


class IKeywordStore(ABC):
    @abstractmethod
    async def save_children(self, nodes: List[ChildNode]) -> bool:
        pass

    @abstractmethod
    async def search_keyword(
        self,
        query: str,
        top_k: int = 5,
        doc_ids: Optional[List[UUID]] = None,
    ) -> List[ScoredNode]:
        pass

    @abstractmethod
    async def delete_children_by_parent_ids(self, parent_ids: List[UUID]) -> bool:
        pass
