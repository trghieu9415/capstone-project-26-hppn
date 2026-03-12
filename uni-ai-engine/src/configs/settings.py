from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Cấu hình gRPC Server
    GRPC_HOST: str = Field(default="[::]", description="Lắng nghe trên mọi IP")
    GRPC_PORT: int = Field(default=50051, description="Cổng chạy gRPC server")
    MAX_WORKERS: int = Field(default=10,
                             description="Số lượng luồng xử lý đồng thời của gRPC")

    # Cấu hình Database (PostgreSQL)
    POSTGRES_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/uni_ai_db",
        description="Chuỗi kết nối đến PostgreSQL"
    )

    # 3. Cấu hình Vector DB (Qdrant)
    QDRANT_URL: str = Field(
        default="http://localhost:6333",
        description="URL của Qdrant server")
    QDRANT_API_KEY: str | None = Field(
        default=None,
        description="API Key của Qdrant (nếu có)")
    QDRANT_COLLECTION: str = Field(
        default="document_chunks",
        description="Tên collection lưu vector")

    # Cấu hình Keyword DB (BM25)
    KEYWORD_DB_DIR: str = Field(
        default="../data/keyword_db",
        description="Thư mục lưu file index của BM25"
    )

    # 5. Cấu hình AI & Embedding Model
    # EMBEDDING_MODEL_NAME: str = Field(default="keepitreal/vietnamese-sbert")
    EMBEDDING_MODEL_NAME: str = Field(default="dangvantuan/vietnamese-embedding")
    VECTOR_SIZE: int = Field(
        default=768,
        description="Kích thước vector của model (sbert là 768)")

    GEMINI_API_KEY: str = Field(default="your_gemini_api_key_here")
    GEMINI_MODEL_NAME: str = Field(default="gemini-2.5-flash-lite")

    CHUNK_SIZE: int = Field(default=500, description="Số lượng từ tối đa trong 1 chunk")
    CHUNK_OVERLAP: int = Field(
        default=50,
        description="Số lượng từ lặp lại giữa 2 chunk liên tiếp")

    # Đọc từ file .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
