from typing import Dict, Any

from core.ingestion.chunker import PDRChunker
from core.ingestion.loader import DocumentLoader
from infrastructure.storage.base import IDocumentStore, IKeywordStore, IVectorStore


class IngestionPipeline:
    def __init__(
        self,
        document_store: IDocumentStore,
        vector_store: IVectorStore,
        keyword_store: IKeywordStore,
        embedding_service: Any,
    ):
        self.doc_store = document_store
        self.vec_store = vector_store
        self.kw_store = keyword_store
        self.embedding_service = embedding_service

        self.loader = DocumentLoader()
        self.chunker = PDRChunker()

    def execute(
        self, file_bytes: bytes, extension: str, metadata: Dict[str, Any]
    ) -> bool:
        try:

            clean_text = self.loader.load_from_bytes(file_bytes, extension)
            if not clean_text:
                print(f"[Warning] Không thể trích xuất text từ file.")
                return False

            parent_nodes, child_nodes = self.chunker.chunk_document(
                clean_text, metadata
            )

            for child in child_nodes:
                child.embedding = self.embedding_service.embed_text(child.text_chunk)

            docs_saved = self.doc_store.save_parents(parent_nodes)
            vecs_saved = self.vec_store.save_children(child_nodes)
            kws_saved = self.kw_store.save_children(child_nodes)

            if docs_saved and vecs_saved and kws_saved:
                print(
                    f"[Info] Index thành công: {len(parent_nodes)} Parents, {len(child_nodes)} Children."
                )
                return True
            else:
                print("[Error] Có lỗi xảy ra trong quá trình lưu xuống các Database.")
                return False

        except Exception as e:
            print(f"[Exception] Lỗi tại Ingestion Pipeline: {e}")
            return False
