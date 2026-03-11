import asyncio
import grpc

from configs.settings import settings
from presentation.dependencies import init_dependencies
from presentation.grpc_servicer import GrpcRagServicer
from utils.logger import app_logger

import rag_service_pb2_grpc as rag_pb2_grpc


async def serve():
    app_logger.info("--- Khởi động UniRAG AI Engine ---")

    # 1. Khởi tạo tất cả Dependencies
    ingestion_pipeline, rag_service = await init_dependencies()

    # 2. Khởi tạo gRPC Server
    server = grpc.aio.server()

    # 3. Gắn Servicer (đã được inject dependencies) vào Server
    rag_pb2_grpc.add_RagEngineServiceServicer_to_server(
        GrpcRagServicer(ingestion_pipeline, rag_service),
        server
    )

    listen_addr = f"{settings.GRPC_HOST}:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)

    app_logger.info(f"gRPC Server đang lắng nghe tại: {listen_addr}")

    await server.start()

    try:
        await server.wait_for_termination()
    except asyncio.CancelledError:
        app_logger.info("Đang dừng gRPC Server...")
        await server.stop(5)  # Chờ 5s để dọn dẹp kết nối


if __name__ == "__main__":
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("\nTiến trình đã được dừng bởi người dùng.")
