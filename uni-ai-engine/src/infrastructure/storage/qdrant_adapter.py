from typing import List, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchValue, MatchAny
)
from infrastructure.storage.base import IVectorStore
from schemas.document import ChildNode, DocumentMetadata
from schemas.request import DocumentFilter
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
            app_logger.info(f"Đang tạo Qdrant Collection: {self.collection_name}")
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size, distance=Distance.COSINE
                ),
            )

            from qdrant_client.models import PayloadSchemaType

            indexes = ["metadata.user_id",
                       "metadata.folder_id",
                       "metadata.document_id",
                       "metadata.tags"]
            for field in indexes:
                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD
                )
            app_logger.info("Đã tạo xong các Payload Indexes cho filter.")

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
                "parent_id": str(node.parent_id),
                "text_chunk": node.text_chunk,
                "metadata": node.metadata.model_dump(),
            }

            points.append(
                PointStruct(id=str(node.id), vector=node.embedding, payload=payload)
            )

        try:
            total_points = len(points)
            for i in range(0, total_points, batch_size):
                batch = points[i: i + batch_size]
                await self.client.upsert(
                    collection_name=self.collection_name, points=batch
                )
                app_logger.info(
                    f"Đã insert batch Qdrant: {min(i + batch_size, total_points)}/{total_points} vectors."
                )

            return True
        except Exception as e:
            app_logger.error(f"Lỗi lưu vector vào Qdrant: {e}")
            return False

    async def search_vector(
        self, query_embedding: List[float], top_k: int = 5,
        filters: Optional[DocumentFilter] = None
    ) -> List[ChildNode]:
        try:
            query_filter = None
            if filters:
                conditions = [FieldCondition(
                    key="metadata.user_id",
                    match=MatchValue(value=filters.user_id))]
                if filters.folder_id:
                    conditions.append(
                        FieldCondition(
                            key="metadata.folder_id",
                            match=MatchValue(value=filters.folder_id))
                    )
                if filters.document_id:
                    conditions.append(
                        FieldCondition(
                            key="metadata.document_id",
                            match=MatchValue(value=filters.document_id))
                    )
                if filters.tags:
                    conditions.append(
                        FieldCondition
                        (key="metadata.tags",
                         match=MatchAny(any=filters.tags))
                    )
                query_filter = Filter(must=conditions)

            search_result = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                query_filter=query_filter
            )

            results = []
            for hit in search_result:
                meta_dict = hit.payload.get("metadata", {})
                if "extra_info" not in meta_dict or meta_dict["extra_info"] is None:
                    meta_dict["extra_info"] = {}
                meta_dict["extra_info"]["vector_score"] = hit.score

                node = ChildNode(
                    id=hit.id,
                    parent_id=hit.payload.get("parent_id", ""),
                    text_chunk=hit.payload.get("text_chunk", ""),
                    embedding=None,
                    metadata=DocumentMetadata(**meta_dict),
                )
                results.append(node)
            return results
        except Exception as e:
            app_logger.error(f"Lỗi khi query Qdrant: {e}")
            return []
