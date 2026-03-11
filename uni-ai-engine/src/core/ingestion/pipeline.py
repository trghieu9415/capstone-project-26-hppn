import asyncio
import uuid
from typing import List, Dict, Any
from uuid import UUID

from core.ingestion.chunker import TextChunker
from core.ingestion.loader import DocumentLoader
from schemas.document import ParentNode, ChildNode
from infrastructure.storage.base import IDocumentStore, IVectorStore, IKeywordStore
from infrastructure.embeddings.base import IEmbeddingService
from utils.logger import app_logger


class IngestionPipeline:
    def __init__(
        self,
        document_store: IDocumentStore,
        vector_store: IVectorStore,
        keyword_store: IKeywordStore,
        embedding_service: IEmbeddingService,
    ):
        self.doc_store = document_store
        self.vector_store = vector_store
        self.keyword_store = keyword_store
        self.embedding_service = embedding_service

        self.loader = DocumentLoader()
        self.chunker = TextChunker()

    @staticmethod
    def _split_text_by_words(text: str, word_limit: int = 1200) -> List[str]:
        words = text.split()
        return [" ".join(words[i: i + word_limit]) for i in
                range(0, len(words), word_limit)]

    async def run(
        self,
        file_bytes: bytes,
        file_name: str,
        extension: str,
        doc_id: UUID,
        metadata: Dict[str, Any] = None
    ) -> bool:
        metadata = metadata or {}
        metadata["file_name"] = file_name

        try:
            app_logger.info(f"==> Bắt đầu nạp tài liệu [ID: {doc_id}]")
            clean_text = self.loader.load_and_clean(file_bytes, extension)

            parent_texts = self._split_text_by_words(clean_text, word_limit=1200)

            parent_nodes: List[ParentNode] = []
            child_nodes: List[ChildNode] = []

            for i, p_text in enumerate(parent_texts):
                parent_chunk_id = uuid.uuid4()

                p_node = ParentNode(
                    id=parent_chunk_id,
                    doc_id=doc_id,
                    full_text=p_text,
                    metadata={**metadata, "chunk_index": i}
                )
                parent_nodes.append(p_node)

                children = self.chunker.split_into_nodes(
                    text=p_text,
                    parent_id=parent_chunk_id,
                    metadata=p_node.metadata
                )
                child_nodes.extend(children)

            if not child_nodes:
                return False

            await self.doc_store.save_parents(parent_nodes)
            app_logger.info(f"Đã lưu {len(parent_nodes)} đoạn parent vào Postgres.")

            texts_to_embed = [node.text_chunk for node in child_nodes]
            embeddings = await self.embedding_service.embed_batch(texts_to_embed)

            for i, node in enumerate(child_nodes):
                node.embedding = embeddings[i]

            success_v, success_k = await asyncio.gather(
                self.vector_store.save_children(child_nodes),
                self.keyword_store.save_children(child_nodes)
            )

            if success_v and success_k:
                app_logger.info(f"==> Hoàn tất nạp tài liệu {file_name} thành công.")
                return True

            app_logger.error("Lỗi lưu trữ tại VectorStore hoặc KeywordStore.")
            return False

        except Exception as e:
            app_logger.error(f"Lỗi Pipeline tại file {file_name}: {e}")
            return False

    async def delete_document(self, doc_id: UUID) -> bool:
        try:
            parent_ids = await self.doc_store.get_parent_ids_by_doc_id(doc_id)

            results = await asyncio.gather(
                self.doc_store.delete_parents([doc_id]),
                self.vector_store.delete_children_by_parent_ids(parent_ids),
                self.keyword_store.delete_children_by_parent_ids(parent_ids)
            )
            return all(results)
        except Exception as e:
            app_logger.error(f"Lỗi khi xóa tài liệu: {e}")
            return False
