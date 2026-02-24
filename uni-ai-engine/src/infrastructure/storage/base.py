from abc import ABC, abstractmethod
from typing import List

from src.schemas.document import ChildNode, ParentNode


class IDocumentStore(ABC):
    @abstractmethod
    def save_parents(self, nodes: List[ParentNode]) -> bool:
        pass

    def get_parents_by_ids(self, parent_ids: List[str]) -> bool:
        pass


class IVectorStore(ABC):
    @abstractmethod
    def save_children(self, nodes: List[ChildNode]) -> bool:
        pass


class IKeywordStore(ABC):
    @abstractmethod
    def save_children(self, nodes: List[ChildNode]) -> bool:
        pass
