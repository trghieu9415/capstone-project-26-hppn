from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID


class BaseNode(BaseModel):
    id: UUID
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParentNode(BaseNode):
    doc_id: UUID
    full_text: str


class ChildNode(BaseNode):
    parent_id: UUID
    chunk_index: int
    text_chunk: str
    embedding: Optional[List[float]] = None


class ScoredNode(BaseModel):
    node: ChildNode
    score: float
