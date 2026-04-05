import asyncio
import math
import re
from dataclasses import dataclass
from typing import List

import torch
from sentence_transformers import CrossEncoder, SentenceTransformer, util
from transformers import pipeline

from configs.settings import settings
from schemas.document import BaseNode, ParentNode, ChildNode


@dataclass
class AnswerQualityMetrics:
    faithfulness: float
    relevance: float


class AnswerEvaluator:
    def __init__(
        self,
        relevance_model: SentenceTransformer,
        nli_model_name: str = settings.NLI_MODEL_NAME,
    ):
        self.relevance_model = relevance_model
        self.faithfulness_model = pipeline(
            "text-classification",
            model=nli_model_name,
            truncation=True,
            max_length=512
        )

    async def evaluate_relevance(self, query: str, answer: str) -> float:
        def _get_similarity():
            embeddings = self.relevance_model.encode(
                [query, answer],
                normalize_embeddings=True,
                convert_to_tensor=True
            )

            cos_sim = util.cos_sim(embeddings[0], embeddings[1])
            return float(cos_sim.item())

        return await asyncio.to_thread(_get_similarity)

    async def evaluate_faithfulness(
        self, context: List[BaseNode],
        answer: str
    ) -> float:
        if not context:
            return 0.0

        clean_answer = answer.replace("Dựa trên thông tin được cung cấp:", "").strip()
        clean_answer = re.sub(r'---\s*\[Nguồn: .*?\]\s*---', '', clean_answer).strip()

        def _run_nli():
            sentences = [s.strip() for s in clean_answer.split('\n') if s.strip()]
            if not sentences: return 0.0

            total_entailment = 0.0

            for sentence in sentences:
                sentence_max_score = 0.0

                for chunk in context:
                    raw_text = chunk.full_text if isinstance(
                        chunk,
                        ParentNode
                    ) else chunk.text_chunk

                    mini_chunks = [raw_text[i:i + 1000] for i in
                                   range(0, len(raw_text), 800)]

                    for mini_text in mini_chunks:
                        result = self.faithfulness_model(
                            {"text": mini_text, "text_pair": sentence},
                            top_k=None,
                            truncation="only_first"
                        )

                        entail_score = next(
                            (item['score'] for item in result if
                             item['label'].lower() == 'entailment'),
                            0.0
                        )

                        sentence_max_score = max(sentence_max_score, entail_score)
                total_entailment += sentence_max_score
            return total_entailment / len(sentences)

        return await asyncio.to_thread(_run_nli)

    async def evaluate_answer(
        self, query: str, answer: str,
        context: List[BaseNode]
    ) -> AnswerQualityMetrics:
        relevance_score = await self.evaluate_relevance(query, answer)
        faithfulness_score = await self.evaluate_faithfulness(context, answer)

        return AnswerQualityMetrics(
            relevance=relevance_score,
            faithfulness=faithfulness_score
        )
