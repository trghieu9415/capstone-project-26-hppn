from typing import List, AsyncGenerator

from schemas.document import ParentNode
from core.generation.prompts import RAGPromptTemplate
from infrastructure.llms.base import ILLMService
from utils.logger import app_logger


class RAGGenerator:
    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service

    async def generate_answer(
        self, query: str, parent_nodes: List[ParentNode], temperature: float = 0.0
    ) -> str:
        app_logger.info(
            f"Bắt đầu tạo câu trả lời cho query: '{query}' với {len(parent_nodes)} tài liệu."
        )

        system_prompt = RAGPromptTemplate.get_system_prompt()
        user_prompt = RAGPromptTemplate.build_user_prompt(query, parent_nodes)

        app_logger.debug("Đã build prompt thành công. Đang gọi LLM...")

        try:
            answer = await self.llm_service.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )
            app_logger.info("LLM đã trả về kết quả thành công.")
            return answer if answer else "Lỗi: LLM trả về kết quả rỗng."

        except Exception as e:
            app_logger.error(f"Lỗi trong quá trình sinh câu trả lời (Generate): {e}")
            return "Hệ thống AI hiện đang bận hoặc gặp sự cố. Vui lòng thử lại sau."

    async def generate_stream(
        self, query: str, parent_nodes: List[ParentNode], temperature: float = 0.0
    ) -> AsyncGenerator[str, None]:
        app_logger.info(f"Bắt đầu mở luồng stream trả lời cho query: '{query}'")

        system_prompt = RAGPromptTemplate.get_system_prompt()
        user_prompt = RAGPromptTemplate.build_user_prompt(query, parent_nodes)

        try:
            async for chunk in self.llm_service.generate_stream(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            ):
                yield chunk

        except Exception as e:
            app_logger.error(f"Lỗi trong quá trình stream câu trả lời: {e}")
            yield "\n[Lỗi hệ thống: Quá trình stream dữ liệu từ AI bị gián đoạn]"
