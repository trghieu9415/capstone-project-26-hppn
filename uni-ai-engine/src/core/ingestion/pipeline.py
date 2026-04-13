import asyncio
import uuid
from typing import List, Dict, Any
from uuid import UUID

from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.ingestion.loader import DocumentLoader
from schemas.document import ParentNode, ChildNode
from infrastructure.storage.base import IDocumentStore, IVectorStore, IKeywordStore
from infrastructure.embeddings.base import IEmbeddingService
from utils.loggers.app_logger import app_logger


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

    @staticmethod
    def _split_text(text: str) -> list[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=6000,
            chunk_overlap=0,
            length_function=len,
            is_separator_regex=False,
            separators=["\n\n", "\n", "."]
        )

        chunks = text_splitter.split_text(text)
        return chunks

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
            app_logger.info(
                f"==> Bắt đầu nạp tài liệu {file_name}{extension} [ID: {doc_id}]")
            clean_text = self.loader.load_and_clean(file_bytes, extension)

            parent_texts = self._split_text(clean_text)
            app_logger.info(f"Tài liệu đã cắt thành {len(parent_texts)} đoạn Parent")

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

                app_logger.info(f"Nhúng và tạo ChildNode {i + 1}/{len(parent_texts)}")
                children = await self.embedding_service.chunk_and_embed(
                    parent_node=p_node,
                    metadata=p_node.metadata
                )
                child_nodes.extend(children)

            if not child_nodes:
                app_logger.warning(f"Không tạo được đoạn Child nào cho {file_name}")
                return False

            await self.vector_store.save_children(child_nodes)
            app_logger.info(
                f"{file_name}: Nhúng & Lưu Qdrant thành công {len(child_nodes)} Nodes.")

            await self.keyword_store.save_children(child_nodes)
            app_logger.info(f"Nạp thành công {file_name} vào KeywordStore (BM25).")

            await self.doc_store.save_parents(parent_nodes)
            app_logger.info(f"Đã lưu {len(parent_nodes)} đoạn parent vào Postgres.")

            app_logger.info(f"==> Lưu thành công {file_name}{extension}.")
            return True

        except Exception as e:
            app_logger.error(f"Lỗi Pipeline tại file {file_name}{extension}: {e}")
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
