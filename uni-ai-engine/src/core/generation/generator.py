from typing import List, AsyncGenerator

from schemas.document import ParentNode, ChildNode
from core.generation.prompts import RAGPromptTemplate
from infrastructure.llms.base import ILLMService
from utils.loggers.app_logger import app_logger


class RAGGenerator:
    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service

    # ================ NAIVE RAG FULL TEXT ================
    async def naive_generate(
        self, query: str,
        child_nodes: List[ChildNode],
        temperature: float = 0.0,
    ) -> str:
        app_logger.info(f"Trả lời cho query: '{query}'")
        system_prompt = RAGPromptTemplate.get_system_prompt()
        user_prompt = RAGPromptTemplate.build_simple_user_prompt(
            query, child_nodes
        )

        try:
            ans = await self.llm_service.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )
            # ans = "Tôi sẽ tạm không trả lời câu hỏi của bạn để đánh giá"
            return "Không có thông tin" if ans is None else ans

        except Exception as e:
            app_logger(f"Lỗi Generate: {e}")

    # ================ FULL TEXT ================
    async def generate(
        self, query: str,
        parent_nodes: List[ParentNode],
        temperature: float = 0.0,
        doc_names=None
    ) -> str:
        if doc_names is None:
            doc_names = {}

        app_logger.info(f"Trả lời cho query: '{query}'")

        system_prompt = RAGPromptTemplate.get_system_prompt()
        user_prompt = RAGPromptTemplate.build_user_prompt(
            query, parent_nodes, doc_names
        )

        try:
            ans = await self.llm_service.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
            )
            # ans = "Tôi sẽ tạm không trả lời câu hỏi của bạn để đánh giá"
            return "Không có thông tin" if ans is None else ans


        except Exception as e:
            app_logger(f"Lỗi Generate: {e}")

    # ================ TEXT STREAM ================
    async def generate_stream(
        self, query: str,
        parent_nodes: List[ParentNode],
        temperature: float = 0.0,
        doc_names=None
    ) -> AsyncGenerator[str, None]:
        if doc_names is None:
            doc_names = {}

        app_logger.info(f"Bắt đầu mở luồng stream trả lời cho query: '{query}'")

        system_prompt = RAGPromptTemplate.get_system_prompt()
        user_prompt = RAGPromptTemplate.build_user_prompt(
            query, parent_nodes, doc_names
        )

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
