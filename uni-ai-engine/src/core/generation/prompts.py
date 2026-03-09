from typing import List
from schemas.document import ParentNode


class RAGPromptTemplate:
    @staticmethod
    def get_system_prompt() -> str:
        return """
            Bạn là một trợ lý AI học thuật chuyên nghiệp.
            Nhiệm vụ của bạn là giải đáp thắc mắc của sinh viên dựa trên dữ liệu từ [NGỮ CẢNH].

            QUY TẮC ỨNG XỬ:
            1. CHỈ sử dụng thông tin được cung cấp trong [NGỮ CẢNH].
            2. Nếu không có thông tin trong tài liệu, hãy trả lời: 'Xin lỗi, hệ thống không tìm thấy thông tin chính xác trong quy chế để trả lời câu hỏi này. Bạn vui lòng liên hệ Phòng Đào tạo để được hỗ trợ chi tiết hơn.'
            3. TRÍCH DẪN NGUỒN: Cuối mỗi đoạn thông tin, hãy ghi rõ nguồn (ví dụ: [Nguồn: Quy-che-dao-tao.pdf]).
            4. ĐỊNH DẠNG: Sử dụng Markdown (bullet points, bảng, in đậm) để thông tin dễ theo dõi.
            5. TÔNG GIỌNG: Lịch sự, chuyên nghiệp, hỗ trợ.
        """

    @staticmethod
    def build_user_prompt(query: str, parent_nodes: List[ParentNode]) -> str:
        if not parent_nodes:
            return f"Câu hỏi: {query}\n\n[NGỮ CẢNH]\nKhông có tài liệu nào liên quan."

        context_parts = []
        for i, node in enumerate(parent_nodes, start=1):
            source_name = node.metadata.get("file_name", f"Tài liệu {i}")
            context_parts.append(
                f"--- Nguồn {i}: {source_name} ---\n{node.full_text}\n"
            )

        context_string = "\n\n".join(context_parts)
        return f"""Dựa vào các tài liệu sau đây, hãy trả lời câu hỏi của người dùng.
            [NGỮ CẢNH]
            {context_string}

            [CÂU HỎI]
            {query}
        """
