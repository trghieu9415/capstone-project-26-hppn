import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from configs.settings import settings
from infrastructure.storage.document_db.postgres_adapter import PostgresAdapter
from infrastructure.storage.vector_db.qdrant_adapter import QdrantAdapter
from schemas.document import ParentNode, ChildNode
from utils.logger import app_logger
import uuid


async def test_db_integration():
    app_logger.info("=== BẮT ĐẦU TEST TÍCH HỢP DB ===")

    # 1. Khởi tạo Adapters từ Settings
    pg_adapter = PostgresAdapter(settings.DATABASE_URL)
    qdrant_adapter = QdrantAdapter(
        collection_name=settings.QDRANT_COLLECTION,
        vector_size=768,  # Kích thước của vietnamese-sbert
        url=settings.QDRANT_URL,
    )

    # 2. Khởi tạo Database (Tạo bảng/collection)
    app_logger.info("Đang khởi tạo Table và Collection...")
    await pg_adapter.init_db()
    await qdrant_adapter.initialize()

    # 3. Tạo dữ liệu mẫu
    p_id = uuid.uuid4()
    parent = ParentNode(
        id=p_id,
        full_text="Nội dung gốc của tài liệu học tập.",
        metadata={"file": "test.pdf"},
    )

    child = ChildNode(
        id=uuid.uuid4(),
        parent_id=p_id,
        text_chunk="Nội dung con đã cắt nhỏ.",
        embedding=[0.1] * 768,  # Dummy vector
        metadata={"file": "test.pdf"},
    )

    # 4. Lưu vào Postgres
    app_logger.info("1. Đang lưu vào Postgres...")
    pg_success = await pg_adapter.save_parents([parent])
    if pg_success:
        app_logger.info("✅ Postgres: OK")

    # 5. Lưu vào Qdrant
    app_logger.info("2. Đang lưu vào Qdrant...")
    qd_success = await qdrant_adapter.save_children([child])
    if qd_success:
        app_logger.info("✅ Qdrant: OK")

    app_logger.info("\n=== BÀI TEST HOÀN TẤT ===")


if __name__ == "__main__":
    # Lệnh chạy Docker trước khi chạy script: docker-compose up -d
    asyncio.run(test_db_integration())
