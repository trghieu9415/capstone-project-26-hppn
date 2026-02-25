from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from uuid import UUID


class BaseNode(BaseModel):
    id: UUID
    info: Dict[str, Any] = Field(default_factory=dict)


class ParentNode(BaseNode):
    full_text: str


class ChildNode(BaseNode):
    parent_id: UUID
    text_chunk: str
    embedding: Optional[List[float]] = None
