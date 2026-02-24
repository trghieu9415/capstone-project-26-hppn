import asyncio
from typing import Dict, Any

from core.ingestion.chunker import PDRChunker
from core.ingestion.loader import DocumentLoader
from infrastructure.storage.base import IDocumentStore, IKeywordStore, IVectorStore
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
        self.vec_store = vector_store
        self.kw_store = keyword_store
        self.embedding_service = embedding_service

        self.loader = DocumentLoader()
        self.chunker = PDRChunker()

    async def execute(
        self, file_bytes: bytes, extension: str, metadata: Dict[str, Any]
    ) -> bool:
        try:
            clean_text = await asyncio.to_thread(
                self.loader.load_and_clean, file_bytes, extension
            )
            if not clean_text:
                app_logger.warning("Không thể trích xuất text từ file.")
                return False

            parent_nodes, child_nodes = await asyncio.to_thread(
                self.chunker.chunk_document, clean_text, metadata
            )

            embed_tasks = [
                self.embedding_service.embed_text(child.text_chunk)
                for child in child_nodes
            ]
            embeddings = await asyncio.gather(*embed_tasks)

            for child, emb in zip(child_nodes, embeddings):
                child.embedding = emb

            docs_saved, vecs_saved, kws_saved = await asyncio.gather(
                self.doc_store.save_parents(parent_nodes),
                self.vec_store.save_children(child_nodes),
                self.kw_store.save_children(child_nodes),
            )

            if docs_saved and vecs_saved and kws_saved:
                app_logger.info(
                    f"Index thành công: {len(parent_nodes)} Parents, {len(child_nodes)} Children."
                )
                return True
            else:
                app_logger.error(
                    "Có lỗi xảy ra trong quá trình lưu xuống các Database."
                )
                return False

        except Exception as e:
            app_logger.error(f"Lỗi tại Ingestion Pipeline: {e}")
            return False
