from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Cấu hình gRPC Server
    GRPC_HOST: str = Field(default="[::]", description="Lắng nghe trên mọi IP")
    GRPC_PORT: int = Field(default=50051, description="Cổng chạy gRPC server")
    MAX_WORKERS: int = Field(default=10)

    # Cấu hình Database (PostgreSQL)
    POSTGRES_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/uni_ai_db")

    # 3. Cấu hình Vector DB (Qdrant)
    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_API_KEY: str | None = Field(default=None)
    QDRANT_COLLECTION: str = Field(default="document_chunks")

    # Cấu hình Keyword DB (BM25)
    KEYWORD_DB_DIR: str = Field(default="data/keyword_db")

    # EMBEDDING_MODEL_NAME: str = Field(default="keepitreal/vietnamese-sbert")
    # EMBEDDING_MODEL_NAME: str = Field(default="dangvantuan/vietnamese-embedding")
    # EMBEDDING_MODEL_NAME: str = Field(default="AITeamVN/Vietnamese_Embedding")
    EMBEDDING_MODEL_NAME: str = Field(
        default="dangvantuan/vietnamese-document-embedding")
    EMBEDDING_BATCH_SIZE: int = Field(default=64)
    CHUNK_SIZE: int = Field(default=256)
    CHUNK_OVERLAP: int = Field(default=50)

    CROSS_ENCODER_MODEL_NAME: str = Field(default="BAAI/bge-reranker-v2-m3")
    NLI_MODEL_NAME: str = Field(default="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")

    VECTOR_SIZE: int = Field(default=768)

    GEMINI_API_KEY: str = Field(default="your_gemini_api_key_here")
    GEMINI_MODEL_NAME: str = Field(default="gemini-2.5-flash-lite")

    # TOP-K
    VECTOR_SEARCH_TOP_K: int = Field(default=15)
    KEYWORD_SEARCH_TOP_K: int = Field(default=15)
    ALPHA_BLENDING_TOP_K: int = Field(default=10)
    CROSS_ENCODER_TOP_K: int = Field(default=6)

    # Đọc từ file .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
