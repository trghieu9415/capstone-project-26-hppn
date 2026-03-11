from uuid import UUID

import rag_service_pb2 as rag_pb2
import rag_service_pb2_grpc as rag_pb2_grpc

from core.ingestion.pipeline import IngestionPipeline
from core.rag_service import RAGService
from utils.logger import app_logger


class GrpcRagServicer(rag_pb2_grpc.RagEngineServiceServicer):
    def __init__(self, ingestion_pipeline: IngestionPipeline, rag_service: RAGService):
        self.pipeline = ingestion_pipeline
        self.rag_service = rag_service

    async def UploadDocument(self, request_iterator, context):
        full_bytes = bytearray()
        doc_id = None
        file_name = "unknown"
        extension = ".pdf"

        try:
            async for request in request_iterator:
                if doc_id is None:
                    doc_id = request.doc_id
                    file_name = request.file_name
                    extension = request.extension

                full_bytes.extend(request.chunk_data)

            app_logger.info(f"Đã nhận đủ {len(full_bytes)} bytes cho DocID: {doc_id}")

            success = await self.pipeline.run(
                file_bytes=bytes(full_bytes),
                file_name=file_name,
                extension=extension,
                doc_id=UUID(doc_id)
            )

            if success:
                return rag_pb2.UploadResponse(
                    success=True,
                    message="Nạp tài liệu thành công!")
            else:
                return rag_pb2.UploadResponse(
                    success=False,
                    message="Lỗi trong quá trình xử lý Pipeline.")

        except Exception as e:
            app_logger.error(f"Lỗi gRPC Upload: {e}")
            return rag_pb2.UploadResponse(success=False, message=str(e))

    async def DeleteDocument(self, request, context):
        try:
            doc_id = UUID(request.doc_id)
            success = await self.pipeline.delete_document(doc_id)

            if success:
                return rag_pb2.DeleteResponse(success=True, message="Đã xóa tài liệu.")
            return rag_pb2.DeleteResponse(
                success=False,
                message="Không tìm thấy tài liệu hoặc lỗi khi xóa.")
        except Exception as e:
            return rag_pb2.DeleteResponse(success=False, message=str(e))

    async def QueryRag(self, request, context):
        try:
            doc_ids = [
                UUID(id_str) for id_str in request.doc_ids
            ] if request.doc_ids else None

            app_logger.info(f"Nhận truy vấn RAG: {request.question}")

            async for text_chunk in self.rag_service.answer_question_stream(
                query=request.question,
                doc_ids=doc_ids
            ):
                yield rag_pb2.QueryResponse(answer_chunk=text_chunk)

        except Exception as e:
            app_logger.error(f"Lỗi gRPC Query: {e}")
            yield rag_pb2.QueryResponse(
                answer_chunk=f"\n[Lỗi hệ thống Python: {str(e)}]")
