import uuid
from typing import List, Dict, Any
from uuid import UUID
from langchain_text_splitters import RecursiveCharacterTextSplitter

from schemas.document import ChildNode, ParentNode
from configs.settings import settings
from utils.loggers.app_logger import app_logger


class TextChunker:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ".", "?", "!", " ", ""],
            length_function=len,
            is_separator_regex=False,
        )
        app_logger.info(
            f"Đã khởi tạo TextChunker (size={chunk_size}, overlap={chunk_overlap})")

    def split_into_nodes(
        self,
        parent_node: ParentNode,
        metadata: Dict[str, Any] = None
    ) -> List[ChildNode]:
        text = parent_node.full_text
        if not text or not text.strip():
            app_logger.warning(
                f"Text rỗng được gửi tới chunker cho parent_id: {parent_node.id}")
            return []

        chunks = self.splitter.split_text(text)

        nodes = []
        metadata = metadata or {}

        for idx, chunk_text in enumerate(chunks):
            node = ChildNode(
                id=uuid.uuid4(),
                doc_id=parent_node.doc_id,
                parent_id=parent_node.id,
                chunk_index=idx,
                text_chunk=chunk_text,
                metadata=metadata.copy()
            )
            nodes.append(node)

        return nodes
