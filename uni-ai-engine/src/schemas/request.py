from pydantic import BaseModel
from typing import Optional, List


class DocumentFilter(BaseModel):
    user_id: str
    document_id: Optional[str] = None
    folder_id: Optional[str] = None
    tags: Optional[List[str]] = None
