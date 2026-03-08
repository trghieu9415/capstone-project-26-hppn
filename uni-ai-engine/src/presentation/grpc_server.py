import sys
import os
import asyncio
import grpc

# ==============================================================================
# BƯỚC QUAN TRỌNG NHẤT: Nạp đường dẫn (Path) để Python tìm thấy các file nội bộ
# ==============================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Thư mục presentation/
SRC_DIR = os.path.dirname(CURRENT_DIR)  # Thư mục src/
GRPC_PB_DIR = os.path.join(CURRENT_DIR, "grpc_pb")  # Thư mục grpc_pb/

# Add 'src' vào hệ thống để gọi được schemas, core, infrastructure...
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

# Add 'grpc_pb' vào hệ thống để fix lỗi import ngầm của file gRPC
if GRPC_PB_DIR not in sys.path:
    sys.path.append(GRPC_PB_DIR)

# ==============================================================================
# BÂY GIỜ MỚI IMPORT CÁC MODULE (Lưu ý: Không dùng 'from presentation.grpc_pb...')
# ==============================================================================
import rag_service_pb2
import rag_service_pb2_grpc

from schemas.document import DocumentMetadata
from schemas.request import DocumentFilter
from presentation.dependencies import container
from utils.logger import app_logger


class AiEngineServiceServicer(rag_service_pb2_grpc.AiEngineServiceServicer):

    async def IngestDocument(self, request, context):
        app_logger.info(
            f"Nhận request IngestDocument: File {request.metadata.file_name}")

        # 1. Parse Metadata từ Protobuf sang Pydantic
        metadata = DocumentMetadata(
            document_id=request.metadata.document_id,
            user_id=request.metadata.user_id,
            file_name=request.metadata.file_name,
            folder_id=request.metadata.folder_id if request.metadata.HasField(
                "folder_id") else None,
            tags=list(request.metadata.tags)
        )

        # 2. Đưa vào Pipeline
        success = await container.ingestion_pipeline.execute(
            file_bytes=request.file_content,
            extension=request.file_extension,
            metadata=metadata
        )

        return rag_service_pb2.IngestResponse(
            success=success,
            message="Xử lý tài liệu thành công" if success else "Có lỗi xảy ra khi xử lý tài liệu"
        )

    async def AskQuestion(self, request, context):
        app_logger.info(
            f"Nhận request AskQuestion: '{request.query}' từ user {request.filter.user_id}")

        # 1. Parse Filter từ Protobuf sang Pydantic
        doc_filter = DocumentFilter(
            user_id=request.filter.user_id,
            document_id=request.filter.document_id if request.filter.HasField(
                "document_id") else None,
            folder_id=request.filter.folder_id if request.filter.HasField(
                "folder_id") else None,
            tags=list(request.filter.tags) if request.filter.tags else None
        )

        # 2. Đưa vào Pipeline
        answer = await container.query_pipeline.execute(
            query=request.query,
            top_k=request.top_k if request.top_k > 0 else 5,
            filters=doc_filter
        )

        return rag_service_pb2.QueryResponse(answer=answer)

    async def AskQuestionStream(self, request, context):
        app_logger.info(f"Nhận request AskQuestionStream: '{request.query}'")

        doc_filter = DocumentFilter(
            user_id=request.filter.user_id,
            document_id=request.filter.document_id if request.filter.HasField(
                "document_id") else None,
            folder_id=request.filter.folder_id if request.filter.HasField(
                "folder_id") else None,
            tags=list(request.filter.tags) if request.filter.tags else None
        )

        async for chunk in container.query_pipeline.execute_stream(
            query=request.query,
            top_k=request.top_k if request.top_k > 0 else 5,
            filters=doc_filter
        ):
            # Stream trả về từng chunk ký tự cho client
            yield rag_service_pb2.QueryStreamResponse(chunk=chunk)


async def serve():
    # Khởi tạo Database (Bảng, Collection) trước khi nhận Request
    await container.initialize_async()

    # Khởi tạo Async Server
    server = grpc.aio.server()
    rag_service_pb2_grpc.add_AiEngineServiceServicer_to_server(
        AiEngineServiceServicer(), server)

    # Lắng nghe tại port 50051 (Port tiêu chuẩn của gRPC)
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    app_logger.info(
        f"🚀 AI Engine gRPC Server đã sẵn sàng và đang chạy tại {listen_addr}...")

    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        app_logger.info("Tắt Server.")
