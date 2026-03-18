import asyncio
from typing import List, Optional, AsyncGenerator, Dict
from uuid import UUID

from core.generation.generator import RAGGenerator
from core.retrieval.hybrid_ranker import HybridRanker
from core.retrieval.keyword_retriever import KeywordRetriever
from core.retrieval.vector_retriever import VectorRetriever
from infrastructure.storage.base import IDocumentStore
from schemas.document import ParentNode
from utils.logger import app_logger


class RAGService:
    def __init__(
        self,
        doc_store: IDocumentStore,
        vector_retriever: VectorRetriever,
        keyword_retriever: KeywordRetriever,
        ranker: HybridRanker,
        generator: RAGGenerator
    ):
        self.doc_store = doc_store
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.ranker = ranker
        self.generator = generator

    async def _get_context_nodes(
        self,
        query: str,
        top_k: int,
        doc_ids: Optional[List[UUID]]
    ) -> List[ParentNode]:
        vector_task = self.vector_retriever.retrieve(
            query, top_k=top_k, doc_ids=doc_ids
        )
        keyword_task = self.keyword_retriever.retrieve(
            query, top_k=top_k, doc_ids=doc_ids
        )
        vector_res, keyword_res = await asyncio.gather(vector_task, keyword_task)

        top_scored_nodes = self.ranker.rerank(
            query,
            vector_res, keyword_res,
            top_k=top_k
        )
        if not top_scored_nodes:
            return []

        unique_parent_ids = list(set(sn.node.parent_id for sn in top_scored_nodes))
        app_logger.info(f"Các parent_id được chọn: {unique_parent_ids}")
        parent_nodes = await self.doc_store.get_parents_by_ids(unique_parent_ids)

        return parent_nodes

    async def answer_question(
        self,
        query: str,
        doc_ids: Optional[List[UUID]] = None,
        top_k: int = 6
    ) -> str:
        parent_nodes = await self._get_context_nodes(query, top_k, doc_ids)
        doc_names = await self.doc_store.get_doc_names_by_parent_ids(
            [node.id for node in parent_nodes]
        )
        return await self.generator.generate(
            query,
            parent_nodes,
            doc_names=doc_names
        )

    async def answer_question_stream(
        self,
        query: str,
        doc_ids: Optional[List[UUID]] = None,
        top_k: int = 6
    ) -> AsyncGenerator[str, None]:
        parent_nodes = await self._get_context_nodes(query, top_k, doc_ids)
        doc_names = await self.doc_store.get_doc_names_by_parent_ids(
            [node.id for node in parent_nodes]
        )
        async for chunk in self.generator.generate_stream(
            query,
            parent_nodes,
            doc_names=doc_names
        ):
            yield chunk
