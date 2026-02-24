from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class BaseNode(BaseModel):
    id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ParentNode(BaseNode):
    full_text: str

class ChildNode(BaseNode):
    parent_id: str
    text_chunk: str
    embedding: Optional[List[float]] = None