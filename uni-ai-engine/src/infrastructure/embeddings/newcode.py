import asyncio
import uuid
from typing import List, Dict, Any, Literal

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

from schemas.document import ChildNode, ParentNode
from infrastructure.embeddings.base import IEmbeddingService
from utils.loggers.app_logger import app_logger
from configs.settings import settings, ThresholdType


class HuggingFaceAdapter(IEmbeddingService):
    def __init__(
        self,
        model_name: str = settings.EMBEDDING_MODEL_NAME,
        threshold_type: ThresholdType = settings.THRESHOLD_TYPE,
        threshold_value: float = settings.THRESHOLD_VALUE
    ):
        app_logger.info(f"Đang tải siêu Model: {model_name} (Chunk & Embed)...")

        self.langchain_embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cuda', 'trust_remote_code': True},
            encode_kwargs={
                'normalize_embeddings': True,
                'batch_size': 32
            },
            show_progress=True
        )

        self.splitter = SemanticChunker(
            self.langchain_embeddings,
            breakpoint_threshold_type=threshold_type,
            breakpoint_threshold_amount=threshold_value
        )

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            return await asyncio.to_thread(
                self.langchain_embeddings.embed_documents, texts
            )
        except Exception as e:
            app_logger.error(f"Lỗi khi tạo batch embedding: {e}")
            return []

    async def embed_query(self, query: str) -> List[float]:
        try:
            return await asyncio.to_thread(
                self.langchain_embeddings.embed_query, query
            )
        except Exception as e:
            app_logger.error(f"Lỗi khi nhúng câu hỏi: {e}")
            return []

    async def embed_text(self, text: str, is_query: bool = False) -> List[float]:
        return await self.embed_query(text) if is_query else \
            (await self.embed_batch([text]))[0]

    async def chunk_and_embed(
        self,
        parent_node: ParentNode,
        metadata: Dict[str, Any] = None
    ) -> List[ChildNode]:
        text = parent_node.full_text
        if not text or not text.strip():
            app_logger.warning(f"Text rỗng cho parent_id: {parent_node.id}")
            return []

        chunks = await asyncio.to_thread(self.splitter.split_text, text)
        if not chunks:
            return []

        embeddings = await self.embed_batch(chunks)

        nodes = []
        metadata = metadata or {}

        for idx, (chunk_text, emb) in enumerate(zip(chunks, embeddings)):
            node = ChildNode(
                id=uuid.uuid4(),
                doc_id=parent_node.doc_id,
                parent_id=parent_node.id,
                chunk_index=idx,
                text_chunk=chunk_text,
                embedding=emb,
                metadata=metadata.copy()
            )
            nodes.append(node)

        return nodes
