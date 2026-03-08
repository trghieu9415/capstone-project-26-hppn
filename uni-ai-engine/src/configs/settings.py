from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = (SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore")
    )
    # Postgres
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/uni_ai_db"
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "uni_documents"

    # LLM & Embeddings
    GEMINI_API_KEY: str = ""
    EMBEDDING_MODEL_NAME: str = "keepitreal/vietnamese-sbert"


settings = Settings()
