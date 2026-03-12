import asyncio
import grpc
import sys
import signal

from configs.settings import settings
from presentation.dependencies import init_dependencies
from presentation.grpc_servicer import GrpcRagServicer
from utils.logger import app_logger

import rag_service_pb2_grpc as rag_pb2_grpc


async def serve():
    app_logger.info("--- Khởi động UniRAG AI Engine ---")

    ingestion_pipeline, rag_service = await init_dependencies()

    server = grpc.aio.server()
    rag_pb2_grpc.add_RagEngineServiceServicer_to_server(
        GrpcRagServicer(ingestion_pipeline, rag_service),
        server
    )

    listen_addr = f"{settings.GRPC_HOST}:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)

    app_logger.info(f"gRPC Server đang lắng nghe tại: {listen_addr}")
    await server.start()
    stop_event = asyncio.Event()

    def _signal_handler():
        app_logger.info("Nhận tín hiệu dừng (SIGINT/SIGTERM)...")
        stop_event.set()

    if sys.platform != 'win32':
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _signal_handler)

    try:
        await stop_event.wait()
    except asyncio.CancelledError:
        app_logger.info("Server bị hủy ngang (KeyboardInterrupt)...")
    finally:
        app_logger.info(
            "Đang dừng gRPC Server (cho phép 5s để hoàn thành các request hiện tại)...")

        await server.stop(grace=5)
        app_logger.info("Đã dọn dẹp xong. Server tắt an toàn!")


if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
    finally:
        print("\nTiến trình đã dừng hoàn toàn.")
