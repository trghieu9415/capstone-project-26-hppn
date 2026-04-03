from typing import List, Optional
from uuid import UUID

from core.generation.generator import RAGGenerator
from core.retrieval.vector_retriever import VectorRetriever
from schemas.document import ChildNode
from utils.evaluator import AnswerEvaluator
from utils.loggers.app_logger import app_logger


class NaiveRAGService:
    def __init__(
        self,
        vector_retriever: VectorRetriever,
        generator: RAGGenerator,
        evaluate_on: bool = False,
        evaluator: AnswerEvaluator = None
    ):
        self.vector_retriever = vector_retriever
        self.generator = generator
        self.evaluate_on = evaluate_on
        self.evaluator = evaluator

    async def _get_context_nodes(
        self,
        query: str,
        doc_ids: Optional[List[UUID]]
    ) -> List[ChildNode]:
        vector_res = await self.vector_retriever.retrieve(
            query, doc_ids=doc_ids
        )

        if not vector_res:
            return []

        return list(map(lambda x: x.node, vector_res))

    async def answer_question(
        self,
        query: str,
        doc_ids: Optional[List[UUID]] = None,
        top_k: int = 6
    ) -> str:
        child_nodes = await self._get_context_nodes(query, doc_ids)
        answer = await self.generator.naive_generate(query, child_nodes)

        if self.evaluate_on:
            results = self.evaluator.evaluate_answer(query, answer, child_nodes)
            app_logger.info(
                f"Faithfulness: {results.faithfulness} - Relevance: {results.relevance}"
            )
        return answer
