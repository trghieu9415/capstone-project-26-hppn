from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID


class DocumentMetadata(BaseModel):
    document_id: str
    user_id: str
    file_name: str
    folder_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    extra_info: Dict[str, Any] = Field(default_factory=dict)


class BaseNode(BaseModel):
    id: UUID
    metadata: DocumentMetadata


class ParentNode(BaseNode):
    full_text: str


class ChildNode(BaseNode):
    parent_id: UUID
    text_chunk: str
    embedding: Optional[List[float]] = None
