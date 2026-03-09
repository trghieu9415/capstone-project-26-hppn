from configs.settings import settings
from infrastructure.storage.postgres_adapter import PostgresAdapter
from infrastructure.storage.qdrant_adapter import QdrantAdapter
from infrastructure.storage.bm25_adapter import BM25Adapter
from infrastructure.embeddings.huggingface_adapter import HuggingFaceAdapter
from infrastructure.llms.gemini_adapter import GeminiAdapter
from core.retrieval.vector_retriever import VectorRetriever
from core.retrieval.keyword_retriever import KeywordRetriever
from core.retrieval.hybrid_ranker import HybridSearcher
from core.generation.generator import RAGGenerator
from core.ingestion.pipeline import IngestionPipeline
from core.rag_service import QueryPipeline
from utils.logger import app_logger


class DependencyContainer:
    def __init__(self):
        self.pg_adapter = PostgresAdapter(settings.DATABASE_URL)
        self.qdrant_adapter = QdrantAdapter(
            collection_name=settings.QDRANT_COLLECTION,
            vector_size=768,
            url=settings.QDRANT_URL,
        )
        self.bm25_adapter = BM25Adapter()

        self.embedding_service = HuggingFaceAdapter(
            model_name=settings.EMBEDDING_MODEL_NAME)
        self.llm_service = GeminiAdapter(api_key=settings.GEMINI_API_KEY)

        self.vector_retriever = VectorRetriever(
            self.qdrant_adapter,
            self.embedding_service)
        self.keyword_retriever = KeywordRetriever(
            self.bm25_adapter)
        self.hybrid_searcher = HybridSearcher(
            self.vector_retriever,
            self.keyword_retriever)

        self.generator = RAGGenerator(self.llm_service)

        self.ingestion_pipeline = IngestionPipeline(
            document_store=self.pg_adapter,
            vector_store=self.qdrant_adapter,
            keyword_store=self.bm25_adapter,
            embedding_service=self.embedding_service
        )
        self.query_pipeline = QueryPipeline(
            hybrid_searcher=self.hybrid_searcher,
            doc_store=self.pg_adapter,
            generator=self.generator
        )

    async def initialize_async(self):
        app_logger.info("Đang kiểm tra và khởi tạo Database...")
        await self.pg_adapter.init_db()
        await self.qdrant_adapter.initialize()
        app_logger.info("Tất cả Database đã sẵn sàng!")


container = DependencyContainer()
