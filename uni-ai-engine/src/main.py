import asyncio
import grpc
import sys
import signal
import threading
import time

from configs.settings import settings
from presentation.dependencies import init_dependencies
from presentation.grpc_servicer import GrpcRagServicer
from utils.logger import app_logger

import presentation.generated.rag_service_pb2_grpc as rag_pb2_grpc


def _listen_for_keypress(stop_event):
    try:
        if sys.platform == 'win32':
            import msvcrt
            while not stop_event.is_set():
                if msvcrt.kbhit():
                    msvcrt.getch()
                    app_logger.info("Bắt được sự kiện nhấn phím (Key Event)...")
                    stop_event.set()
                    break
                time.sleep(0.1)
        else:
            import select
            while not stop_event.is_set():
                i, o, e = select.select([sys.stdin], [], [], 0.1)
                if i:
                    sys.stdin.readline()
                    app_logger.info("Bắt được sự kiện phím bấm...")
                    stop_event.set()
                    break
    except Exception:
        pass


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
    app_logger.info("Bấm phím bất kỳ hoặc [Ctrl + C] để tắt Server.")
    await server.start()

    stop_event = asyncio.Event()

    def _signal_handler():
        app_logger.info("Nhận tín hiệu dừng (SIGINT/SIGTERM)...")
        stop_event.set()

    if sys.platform != 'win32':
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _signal_handler)

    threading.Thread(target=_listen_for_keypress, args=(stop_event,),
                     daemon=True).start()

    try:
        while not stop_event.is_set():
            await asyncio.sleep(0.2)

    except asyncio.CancelledError:
        app_logger.info("Server bị hủy ngang (KeyboardInterrupt)...")
    finally:
        app_logger.info(
            "Đang dừng gRPC Server (cho phép 2s để hoàn thành request hiện tại)...")

        await server.stop(grace=2)
        app_logger.info("END SESSION!")


if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        asyncio.run(serve())
    except KeyboardInterrupt:
        pass
    finally:
        print("\nTiến trình đã dừng hoàn toàn.")
