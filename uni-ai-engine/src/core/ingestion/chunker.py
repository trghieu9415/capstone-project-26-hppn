import uuid
from typing import List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter

from schemas.document import ChildNode, ParentNode, DocumentMetadata
from utils.logger import app_logger


class PDRChunker:
    def __init__(
        self,
        parent_chunk_size: int = 2000,
        parent_chunk_overlap: int = 200,
        child_chunk_size: int = 400,
        child_chunk_overlap: int = 50,
    ):
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=parent_chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", " ", ""],
        )

        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=child_chunk_overlap,
            separators=["\n", ".", "!", "?", ",", " ", ""],
        )

    def chunk_document(
        self, clean_text: str, source_metadata: DocumentMetadata
    ) -> Tuple[List[ParentNode], List[ChildNode]]:
        app_logger.info("Bắt đầu cắt văn bản (Smart Chunking)...")
        parent_nodes = []
        child_nodes = []

        parent_texts = self.parent_splitter.split_text(clean_text)

        for p_text in parent_texts:
            p_id = uuid.uuid4()
            parent_node = ParentNode(
                id=p_id,
                full_text=p_text,
                metadata=source_metadata.model_copy(deep=True)
            )
            parent_nodes.append(parent_node)

            child_texts = self.child_splitter.split_text(p_text)

            for c_text in child_texts:
                c_id = uuid.uuid4()
                child_node = ChildNode(
                    id=c_id,
                    parent_id=p_id,
                    text_chunk=c_text,
                    metadata=source_metadata.model_copy(deep=True),
                )
                child_nodes.append(child_node)

        app_logger.info(
            f"Đã tạo {len(parent_nodes)} Parents và {len(child_nodes)} Children."
        )
        return parent_nodes, child_nodes
