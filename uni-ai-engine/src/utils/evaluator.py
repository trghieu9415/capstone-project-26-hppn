import math
from dataclasses import dataclass
from typing import List

from sentence_transformers import CrossEncoder
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
        encoder_model_name: str = settings.CROSS_ENCODER_MODEL_NAME,
        nli_model_name: str = settings.NLI_MODEL_NAME,
    ):
        self.relevance_model = CrossEncoder(encoder_model_name, max_length=512)
        self.faithfulness_model = pipeline(
            "text-classification",
            model=nli_model_name,
            truncation=True,
            max_length=512
        )

    @staticmethod
    def _sigmoid(x: float) -> float:
        try:
            return 1 / (1 + math.exp(-x))
        except OverflowError:
            return 0.0 if x < 0 else 1.0

    def evaluate_relevance(self, query: str, answer: str) -> float:
        sentence_pair = [[query, answer]]
        raw_score = self.relevance_model.predict(sentence_pair)[0]
        relevance_score = self._sigmoid(float(raw_score))
        return relevance_score

    def evaluate_faithfulness(self, context: List[BaseNode], answer: str) -> float:
        text_context = ""
        if context and isinstance(context[0], ParentNode):
            text_context = "\n\n".join(parent.full_text for parent in context)
        elif context and isinstance(context[0], ChildNode):
            text_context = "\n\n".join(child.text_chunk for child in context)

        results = self.faithfulness_model({
            "text": text_context,
            "text_pair": answer
        }, top_k=None)

        return next(
            (item['score'] for item in results if item['label'] == 'entailment'),
            0.0
        )

    def evaluate_answer(
        self, query: str, answer: str,
        context: List[BaseNode]
    ) -> AnswerQualityMetrics:
        relevance_score = self.evaluate_relevance(query, answer)
        faithfulness_score = self.evaluate_faithfulness(context, answer)
        return AnswerQualityMetrics(relevance_score, faithfulness_score)
