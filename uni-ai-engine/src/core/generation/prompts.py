from typing import List, Dict
from uuid import UUID

from schemas.document import ParentNode, ChildNode
from utils.logger import app_logger


class RAGPromptTemplate:
    @staticmethod
    def get_system_prompt() -> str:
        return """
            Bạn là một trợ lý AI học thuật chuyên nghiệp, nhiệm vụ của bạn là giải đáp thắc mắc của người dùng một cách chính xác dựa trên các tài liệu được cung cấp trong phần [NGỮ CẢNH].
            HÃY TUÂN THỦ NGHIÊM NGẶT CÁC QUY TẮC SAU:

            1. ƯU TIÊN NGỮ CẢNH (RAG FIRST):
            - Luôn phân tích và tổng hợp câu trả lời dựa trên [NGỮ CẢNH]. Không sao chép máy móc mà hãy diễn đạt lại cho dễ hiểu.

            2. YÊU CẦU TRÍCH DẪN (CITATION):
            - Khi đưa ra thông tin, HÃY cố gắng chỉ rõ nguồn tài liệu tại vị trí cuối phần trả lời.
            - Chỉ sử dụng <Tên_Tài_Liệu> có sẵn trong các thẻ `--- [Nguồn: ...] ---`.
            - TUYỆT ĐỐI KHÔNG tự bịa nguồn.

            3. XỬ LÝ KHI THIẾU THÔNG TIN (FALLBACK LOGIC):
            - NẾU [NGỮ CẢNH] không chứa thông tin để trả lời, BẮT BUỘC phải thông báo trước: "Tài liệu hiện tại không chứa thông tin để trả lời câu hỏi này."
            - SAU ĐÓ, bạn được phép sử dụng kiến thức nền tảng của mình để hỗ trợ, nhưng BẮT BUỘC phải mở đầu bằng câu: "Tuy nhiên, theo kiến thức chung (chỉ mang tính tham khảo): ..."

            4. ĐỊNH DẠNG ĐẦU RA:
            - Sử dụng Markdown chuyên nghiệp (Bullet points, in đậm từ khóa, tạo bảng nếu cần so sánh dữ liệu).
            - Văn phong khách quan, lịch sự và mang tính học thuật.
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
            source_name = doc_names[node.id] or f"Tài liệu {i}"
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
