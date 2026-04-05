import asyncio
from typing import List, Optional, AsyncGenerator
from uuid import UUID

from core.generation.generator import RAGGenerator
from core.retrieval.hybrid_ranker import HybridRanker
from core.retrieval.model_ranker import CrossEncoderReranker
from core.retrieval.keyword_retriever import KeywordRetriever
from core.retrieval.vector_retriever import VectorRetriever
from infrastructure.storage.base import IDocumentStore
from schemas.document import ParentNode
from utils.evaluator import AnswerEvaluator
from utils.loggers.app_logger import app_logger
from utils.loggers.retrieval_logger import retrieval_logger


class RAGService:
    def __init__(
        self,
        doc_store: IDocumentStore,
        vector_retriever: VectorRetriever,
        keyword_retriever: KeywordRetriever,
        hybrid_ranker: HybridRanker,
        cross_encoder_ranker: CrossEncoderReranker,
        generator: RAGGenerator,
        evaluate_on: bool = False,
        evaluator: AnswerEvaluator = None
    ):
        self.doc_store = doc_store
        self.vector_retriever = vector_retriever
        self.keyword_retriever = keyword_retriever
        self.hybrid_ranker = hybrid_ranker
        self.cross_encoder_ranker = cross_encoder_ranker
        self.generator = generator
        self.evaluate_on = evaluate_on
        self.evaluator = evaluator

    async def _get_context_nodes(
        self,
        query: str,
        doc_ids: Optional[List[UUID]]
    ) -> List[ParentNode]:
        vector_task = self.vector_retriever.retrieve(
            query, doc_ids=doc_ids
        )
        keyword_task = self.keyword_retriever.retrieve(
            query, doc_ids=doc_ids
        )
        vector_res, keyword_res = await asyncio.gather(vector_task, keyword_task)

        retrieval_logger.log_vector_search(query, vector_res)
        retrieval_logger.log_keyword_search(query, keyword_res)

        hybrid_nodes = self.hybrid_ranker.rerank(
            vector_res, keyword_res
        )

        retrieval_logger.log_hybrid_search(query, hybrid_nodes)

        final_nodes = self.cross_encoder_ranker.rerank(
            query, hybrid_nodes
        )

        retrieval_logger.log_cross_encoder(query, final_nodes)

        if not final_nodes:
            return []

        unique_parent_ids = list(set(sn.node.parent_id for sn in final_nodes))
        parent_nodes = await self.doc_store.get_parents_by_ids(unique_parent_ids)
        return parent_nodes

    async def answer_question(
        self,
        query: str,
        doc_ids: Optional[List[UUID]] = None,
    ) -> str:
        parent_nodes = await self._get_context_nodes(query, doc_ids)
        doc_names = await self.doc_store.get_doc_names_by_parent_ids(
            [node.id for node in parent_nodes]
        )
        answer = await self.generator.generate(
            query,
            parent_nodes,
            doc_names=doc_names
        )

        if self.evaluate_on:
            results = await self.evaluator.evaluate_answer(query, answer, parent_nodes)
            app_logger.info(
                f"Faithfulness: {results.faithfulness} - Relevance: {results.relevance}"
            )
        return answer

    async def answer_question_stream(
        self,
        query: str,
        doc_ids: Optional[List[UUID]] = None,
    ) -> AsyncGenerator[str, None]:
        parent_nodes = await self._get_context_nodes(query, doc_ids)
        doc_names = await self.doc_store.get_doc_names_by_parent_ids(
            [node.id for node in parent_nodes]
        )
        async for chunk in self.generator.generate_stream(
            query,
            parent_nodes,
            doc_names=doc_names
        ):
            yield chunk
