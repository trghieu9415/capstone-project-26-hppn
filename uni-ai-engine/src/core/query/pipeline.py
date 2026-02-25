from typing import AsyncGenerator
from core.retrieval.hybrid_searcher import HybridSearcher
from core.generation.generator import RAGGenerator
from infrastructure.storage.base import IDocumentStore
from utils.logger import app_logger


class QueryPipeline:
    def __init__(
        self,
        hybrid_searcher: HybridSearcher,
        doc_store: IDocumentStore,
        generator: RAGGenerator,
    ):
        self.hybrid_searcher = hybrid_searcher
        self.doc_store = doc_store
        self.generator = generator

    async def execute(self, query: str, top_k: int = 5) -> str:
        try:
            app_logger.info(f"Đang tìm kiếm tài liệu cho câu hỏi: {query}")
            child_nodes = await self.hybrid_searcher.search(query, top_k=top_k)

            if not child_nodes:
                return "Tôi không tìm thấy thông tin liên quan trong tài liệu học tập của bạn."

            parent_ids = list(set([node.parent_id for node in child_nodes]))
            parent_nodes = await self.doc_store.get_parents_by_ids(parent_ids)

            app_logger.info(
                f"Đã tìm thấy {len(parent_nodes)} ngữ cảnh. Đang tạo câu trả lời..."
            )
            answer = await self.generator.generate_answer(query, parent_nodes)
            return answer

        except Exception as e:
            app_logger.error(f"Lỗi trong Query Pipeline: {e}")
            return "Xin lỗi, đã có lỗi xảy ra trong quá trình xử lý câu hỏi của bạn."

    async def execute_stream(
        self, query: str, top_k: int = 5
    ) -> AsyncGenerator[str, None]:
        try:
            child_nodes = await self.hybrid_searcher.search(query, top_k=top_k)
            if not child_nodes:
                yield "Tôi không tìm thấy thông tin liên quan."
                return

            parent_ids = list(set([node.parent_id for node in child_nodes]))
            parent_nodes = await self.doc_store.get_parents_by_ids(parent_ids)

            async for chunk in self.generator.generate_stream(query, parent_nodes):
                yield chunk

        except Exception as e:
            app_logger.error(f"Lỗi Stream trong Query Pipeline: {e}")
            yield "[Lỗi hệ thống]"
