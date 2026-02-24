from abc import ABC, abstractmethod
from typing import List
from schemas.document import ChildNode, ParentNode


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


class IKeywordStore(ABC):
    @abstractmethod
    async def save_children(self, nodes: List[ChildNode]) -> bool:
        pass
