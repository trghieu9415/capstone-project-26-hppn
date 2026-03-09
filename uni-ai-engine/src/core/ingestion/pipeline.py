import asyncio
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

    async def run(
        self,
        file_bytes: bytes,
        file_name: str,
        extension: str,
        parent_id: UUID,
        metadata: Dict[str, Any] = None
    ) -> bool:
        metadata = metadata or {}
        metadata["file_name"] = file_name

        try:
            app_logger.info(f"==> Bắt đầu nạp tài liệu [ID: {parent_id}]")
            clean_text = self.loader.load_and_clean(file_bytes, extension)

            parent_node = ParentNode(
                id=parent_id,
                full_text=clean_text,
                metadata=metadata
            )
            await self.doc_store.save_parents([parent_node])
            app_logger.info("-> Đã lưu text gốc vào Postgres.")

            child_nodes: List[ChildNode] = self.chunker.split_into_nodes(
                text=clean_text,
                parent_id=parent_id,
                metadata=metadata
            )
            if not child_nodes:
                return False

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

    async def delete_document(self, parent_id: UUID) -> bool:
        try:
            parent_ids = [parent_id]

            results = await asyncio.gather(
                self.doc_store.delete_parents(parent_ids),
                self.vector_store.delete_children_by_parent_ids(parent_ids),
                self.keyword_store.delete_children_by_parent_ids(parent_ids)
            )
            return all(results)
        except Exception as e:
            app_logger.error(f"Lỗi khi xóa tài liệu {parent_id}: {e}")
            return False
