import time

from transformers import pipeline

# Load model NLI
nli_model = pipeline(
    "text-classification",
    model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
    # return_all_scores=True
)

context = """
    để test Faithfulness thì phải so với cái ngữ cảnh nhập từ danh sách parentdocumet
    được gửi lên đúng chứ?
    """
answer = """
Chuẩn không cần chỉnh luôn bro!
"""

start = time.perf_counter()
result = nli_model({
    "text": context,
    "text_pair": answer
}, top_k=None)
end = time.perf_counter()

entailment_score = next(
    (item['score'] for item in result if item['label'] == 'entailment'),
    0.0
)

print(f"Time: {end - start}s")
print(f"Điểm Faithfulness: {entailment_score:.4f}")
print(result)

# scores = {item['label']: item['score'] for item in result[0]}

# faithfulness = scores["entailment"]
# contradiction = scores["contradiction"]

# print({
#     "faithfulness": faithfulness,
#     "contradiction": contradiction
# })


# Kết quả mong đợi: [{'label': 'contradiction', 'score': 0.99...}] -> Bắt được lỗi Hallucination!
