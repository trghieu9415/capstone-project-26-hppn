from typing import List
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from infrastructure.storage.base import IVectorStore
from schemas.document import ChildNode
from utils.logger import app_logger


class QdrantAdapter(IVectorStore):
    def __init__(self, collection_name: str, vector_size: int, url: str):
        self.collection_name = collection_name
        self.client = AsyncQdrantClient(url=url)
        self.vector_size = vector_size

    async def initialize(self):
        collections = await self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        if not exists:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size, distance=Distance.COSINE
                ),
            )

    async def save_children(
        self, nodes: List[ChildNode], batch_size: int = 100
    ) -> bool:
        if not nodes:
            return True

        points = []
        for node in nodes:
            if not node.embedding:
                app_logger.warning(f"Node {node.id} không có embedding, bỏ qua.")
                continue

            payload = {
                "parent_id": node.parent_id,
                "text_chunk": node.text_chunk,
                "info": node.info,
            }

            points.append(
                PointStruct(id=node.id, vector=node.embedding, payload=payload)
            )

        try:
            total_points = len(points)
            for i in range(0, total_points, batch_size):
                batch = points[i : i + batch_size]
                await self.client.upsert(
                    collection_name=self.collection_name, points=batch
                )
                app_logger.info(
                    f"Đã insert batch Qdrant: {i + len(batch)}/{total_points} vectors."
                )

            return True
        except Exception as e:
            app_logger.error(f"Lỗi lưu vector vào Qdrant: {e}")
            return False

    async def search_vector(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[ChildNode]:
        try:
            search_result = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
            )
            results = []
            for hit in search_result:
                node = ChildNode(
                    id=str(hit.id),
                    parent_id=hit.payload.get("parent_id", ""),
                    text_chunk=hit.payload.get("text_chunk", ""),
                    embedding=None,
                    metadata={"vector_score": hit.score},
                )
                results.append(node)
            return results
        except Exception as e:
            app_logger.error(f"Lỗi khi query Qdrant: {e}")
            return []
