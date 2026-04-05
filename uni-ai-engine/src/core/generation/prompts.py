from typing import List, Dict
from uuid import UUID

from schemas.document import ParentNode, ChildNode


class RAGPromptTemplate:
    @staticmethod
    def get_system_prompt() -> str:
        return """
            {
              "role": "Document Manager AI Assistant",
              "objective": "Giải đáp thắc mắc chính xác dựa trên [NGỮ CẢNH] được cung cấp.",
              "strict_rules": {
                "rag_priority": {
                  "principle": "RAG FIRST",
                  "action": "Phân tích và tổng hợp từ [NGỮ CẢNH]. Diễn đạt lại tự nhiên, tránh sao chép máy móc."
                },
                "citation": {
                  "requirement": "Chỉ trích dẫn nguồn có sẵn trong thẻ '--- [Nguồn: ...] ---' ở cuối câu trả lời.",
                  "format": "<Tên_Tài_Liệu>",
                  "prohibition": "TUYỆT ĐỐI KHÔNG tự bịa nguồn."
                },
                "fallback_logic": {
                  "condition": "Nếu [NGỮ CẢNH] không chứa thông tin",
                  "step_1": "Bắt buộc thông báo: 'Tài liệu hiện tại không chứa thông tin để trả lời câu hỏi này.'",
                  "step_2": "Hỗ trợ bằng kiến thức nền bằng cách mở đầu: 'Tuy nhiên, theo kiến thức chung (chỉ mang tính tham khảo): ...'"
                },
                "output_format": {
                  "style": "Markdown (Bullet points, Bold keywords, Tables)",
                  "tone": "Khách quan, lịch sự, học thuật"
                }
              }
            }
        """

    @staticmethod
    def build_user_prompt(
        query: str,
        parent_nodes: List[ParentNode],
        doc_names: Dict[UUID, str]
    ) -> str:
        if not parent_nodes:
            return f"Câu hỏi: {query}\n\n[NGỮ CẢNH]\nKhông có tài liệu nào liên quan."

        context_parts = []
        for i, node in enumerate(parent_nodes, start=1):
            context_parts.append(
                f"--- [Nguồn: {node.metadata["file_name"]}] ---\n{node.full_text}\n"
            )

        context_string = "\n\n".join(context_parts)
        return f"""Dựa vào các tài liệu sau đây, hãy trả lời câu hỏi của người dùng.
            [NGỮ CẢNH]
            {context_string}

            [CÂU HỎI]
            {query}
        """

    @staticmethod
    def build_simple_user_prompt(
        query: str,
        child_nodes: List[ChildNode]
    ) -> str:
        if not child_nodes:
            return f"Câu hỏi: {query}\n\n[NGỮ CẢNH]\nKhông có tài liệu nào liên quan."

        context_parts = []
        for i, node in enumerate(child_nodes, start=1):
            context_parts.append(
                f"--- Nguồn {i} ---\n{node.text_chunk}\n"
            )
        context_string = "\n\n".join(context_parts)
        return f"""Dựa vào các tài liệu sau đây, hãy trả lời câu hỏi của người dùng.
            [NGỮ CẢNH]
            {context_string}

            [CÂU HỎI]
            {query}
        """
