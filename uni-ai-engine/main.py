import os
import sys
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.utils.logger import app_logger
from src.utils.parsers.pdf_parser import PdfParser
from src.utils.text_processing import clean_text_pipeline
from src.core.ingestion.chunker import PDRChunker
from src.infrastructure.embeddings.huggingface_adapter import HuggingFaceAdapter


async def test_pdf_to_embedding(pdf_path: str):
    app_logger.info(f"=== BẮT ĐẦU BÀI TEST VỚI FILE: {pdf_path} ===")

    # 1. Kiểm tra file tồn tại
    if not os.path.exists(pdf_path):
        app_logger.error(f"Không tìm thấy file {pdf_path}. Vui lòng kiểm tra lại!")
        return

    # 2. Đọc file dưới dạng Bytes
    app_logger.info("1. Đang đọc file PDF...")
    with open(pdf_path, "rb") as f:
        file_bytes = f.read()

    # 3. Trích xuất Text từ PDF
    app_logger.info("2. Đang trích xuất văn bản (Extract Text)...")
    parser = PdfParser()
    raw_text = parser.extract_text(file_bytes)

    if not raw_text:
        app_logger.error(
            "Không thể trích xuất chữ từ PDF. File có thể là ảnh scan chưa qua OCR."
        )
        return

    app_logger.info(f"   -> Đã trích xuất được {len(raw_text)} ký tự.")

    # 4. Làm sạch Text
    app_logger.info("3. Đang làm sạch văn bản (Clean Text)...")
    clean_text = clean_text_pipeline(raw_text)

    # 5. Cắt văn bản (Chunking)
    app_logger.info("4. Đang cắt văn bản (Smart Chunking)...")
    chunker = PDRChunker(
        parent_chunk_size=1000, child_chunk_size=200
    )  # Cắt nhỏ để test nhanh
    metadata = {"filename": os.path.basename(pdf_path)}

    parent_nodes, child_nodes = chunker.chunk_document(clean_text, metadata)
    app_logger.info(
        f"   -> Đã cắt thành {len(parent_nodes)} Parents và {len(child_nodes)} Children."
    )

    if not child_nodes:
        app_logger.warning("Không có child_nodes nào được tạo ra.")
        return

    # 6. Khởi tạo Mô hình Embedding (Tải model nếu là lần đầu tiên)
    app_logger.info(
        "5. Khởi tạo HuggingFaceAdapter (Có thể mất vài phút ở lần chạy đầu để tải Model)..."
    )
    embedding_service = HuggingFaceAdapter(model_name="keepitreal/vietnamese-sbert")

    # 7. Test Embedding cho 3 Child Chunk đầu tiên
    app_logger.info("6. Đang tạo Vector Embedding cho 3 đoạn văn bản đầu tiên...")

    test_nodes = child_nodes[:3]
    for i, node in enumerate(test_nodes, 1):
        app_logger.info(f"\n--- Đang xử lý Chunk {i} ---")
        app_logger.info(f"Nội dung: {node.text_chunk[:100]}... (đã cắt ngắn)")

        # Gọi hàm async embed_text (hàm này chúng ta đã sửa dùng asyncio.to_thread ở phần trước)
        vector = await embedding_service.embed_text(node.text_chunk)

        if vector:
            app_logger.info(
                f"✅ Thành công! Vector có chiều dài: {len(vector)} dimensions."
            )
            app_logger.info(f"   Giá trị 5 số đầu tiên của Vector: {vector[:5]}")
        else:
            app_logger.error("❌ Thất bại! Không tạo được Vector.")

    app_logger.info("\n=== BÀI TEST HOÀN TẤT THÀNH CÔNG! ===")


if __name__ == "__main__":
    # Tên file PDF bạn muốn test (để cùng thư mục với main.py)
    PDF_FILE_NAME = "OnTapQTM.pdf"

    # Chạy vòng lặp sự kiện bất đồng bộ
    asyncio.run(test_pdf_to_embedding(PDF_FILE_NAME))
