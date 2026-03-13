from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from configs.settings import settings
from core.generation.generator import RAGGenerator
from core.ingestion.pipeline import IngestionPipeline
from core.rag_service import RAGService
from core.retrieval.algorithm_ranker import HybridRanker
from core.retrieval.keyword_retriever import KeywordRetriever
from core.retrieval.vector_retriever import VectorRetriever

from infrastructure.storage.postgres_adapter import PostgresDocumentStore, Base
from infrastructure.storage.qdrant_adapter import QdrantAdapter
from infrastructure.storage.bm25_adapter import BM25KeywordStore
from infrastructure.embeddings.huggingface_adapter import HuggingFaceAdapter
from infrastructure.llms.gemini_adapter import GeminiService


async def init_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("--- Database: Đã kiểm tra và khởi tạo các bảng thành công ---")


async def init_dependencies():
    # --- A. Khởi tạo Database (Postgres Async) ---
    engine = create_async_engine(settings.POSTGRES_URL, echo=False)
    await init_db(engine)
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

    # --- B. Khởi tạo Infrastructure Adapters ---
    doc_store = PostgresDocumentStore(session_factory=session_factory)

    vector_store = QdrantAdapter(
        collection_name=settings.QDRANT_COLLECTION,
        vector_size=settings.VECTOR_SIZE,
        url=settings.QDRANT_URL
    )
    await vector_store.initialize()

    keyword_store = BM25KeywordStore(persist_dir=settings.KEYWORD_DB_DIR)

    embedding_service = HuggingFaceAdapter(model_name=settings.EMBEDDING_MODEL_NAME)

    llm_service = GeminiService(
        api_key=settings.GEMINI_API_KEY,
        model_name=settings.GEMINI_MODEL_NAME
    )

    # --- C. Khởi tạo Nghiệp vụ (Pipeline & Retrieval) ---
    ingestion_pipeline = IngestionPipeline(
        document_store=doc_store,
        vector_store=vector_store,
        keyword_store=keyword_store,
        embedding_service=embedding_service
    )

    vector_retriever = VectorRetriever(vector_store, embedding_service)
    keyword_retriever = KeywordRetriever(keyword_store)
    ranker = HybridRanker()
    generator = RAGGenerator(llm_service)

    rag_service = RAGService(
        doc_store=doc_store,
        vector_retriever=vector_retriever,
        keyword_retriever=keyword_retriever,
        ranker=ranker,
        generator=generator
    )

    return ingestion_pipeline, rag_service
