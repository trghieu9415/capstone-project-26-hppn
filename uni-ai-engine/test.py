from configs.settings import settings
from infrastructure.embeddings.huggingface_adapter import HuggingFaceAdapter
from utils.evaluator import AnswerEvaluator

embedding_service = HuggingFaceAdapter(model_name=settings.EMBEDDING_MODEL_NAME)
evaluator = AnswerEvaluator(embedding_service.model)

context = file.read("__.txt")

res = await evaluator.evaluate_faithfulness(context, )

print()
