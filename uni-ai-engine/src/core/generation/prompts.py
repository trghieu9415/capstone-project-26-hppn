from typing import List
from schemas.document import ParentNode


class RAGPromptTemplate:
    @staticmethod
    def get_system_prompt() -> str:
        return """
            Bạn là một trợ lý AI học thuật chuyên nghiệp, có nhiệm vụ trả lời câu hỏi dựa trên 
            các tài liệu ngữ cảnh được cung cấp.
            Tuân thủ nghiêm ngặt các quy tắc sau:
            1. CHỈ sử dụng thông tin từ phần [NGỮ CẢNH] để trả lời.
            2. Nếu phần [NGỮ CẢNH] không chứa thông tin để trả lời, hãy nói rõ: 
            'Tôi không tìm thấy đủ thông tin trong tài liệu để trả lời câu hỏi này'. 
            Tuyệt đối không tự bịa đặt (hallucinate).
            3. Câu trả lời cần súc tích, rõ ràng, và trình bày bằng Markdown (dùng bullet points, in đậm từ khóa nếu cần).
        """

    @staticmethod
    def build_user_prompt(query: str, parent_nodes: List[ParentNode]) -> str:
        if not parent_nodes:
            return f"Câu hỏi: {query}\n\n[NGỮ CẢNH]\nKhông có tài liệu nào liên quan được tìm thấy."

        context_parts = []
        for i, node in enumerate(parent_nodes, start=1):
            source_name = node.metadata.get("filename", f"Tài liệu {i}")
            context_parts.append(
                f"--- Bắt đầu nguồn: {source_name} ---\n{node.full_text}\n--- Kết thúc nguồn ---"
            )

        context_string = "\n\n".join(context_parts)
        return f"Vui lòng trả lời câu hỏi sau:\nCâu hỏi: {query}\n\n[NGỮ CẢNH]\n{context_string}"
