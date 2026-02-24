import uuid
from typing import List, Tuple, Dict, Any

from schemas.document import ChildNode, ParentNode


class PDRChunker:
    def __init__(
        self, parent_word_size: int = 400, child_word_size: int = 100, overlap: int = 20
    ):
        self.parent_size = parent_word_size
        self.child_size = child_word_size
        self.overlap = overlap

    def _split_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i : i + chunk_size]
            chunks.append(" ".join(chunk_words))
            i += chunk_size - chunk_overlap

            if chunk_size - chunk_overlap <= 0:
                break

        return chunks

    def chunk_document(
        self, clean_text: str, source_metadata: Dict[str, Any]
    ) -> Tuple[List[ParentNode], List[ChildNode]]:
        parent_nodes = []
        child_nodes = []

        parent_texts = self._split_text(clean_text, self.parent_size, self.overlap)

        for p_text in parent_texts:
            p_id = str(uuid.uuid4())

            parent_node = ParentNode(
                id=p_id, full_text=p_text, metadata=source_metadata.copy()
            )
            parent_nodes.append(parent_node)

            c_overlap = min(self.overlap, int(self.child_size / 2))
            child_texts = self._split_text(p_text, self.child_size, c_overlap)

            for c_text in child_texts:
                c_id = str(uuid.uuid4())
                child_node = ChildNode(
                    id=c_id,
                    parent_id=p_id,
                    text_chunk=c_text,
                    metadata=source_metadata.copy(),
                )
                child_nodes.append(child_node)

        return parent_nodes, child_nodes
