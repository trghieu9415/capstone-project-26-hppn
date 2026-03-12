import asyncio
from typing import List, Optional, Any, cast
from uuid import UUID
from qdrant_client import AsyncQdrantClient, models

from infrastructure.storage.base import IVectorStore
from schemas.document import ChildNode, ScoredNode
from configs.settings import settings
from utils.logger import app_logger


class QdrantAdapter(IVectorStore):
    def __init__(
        self,
        collection_name: str = "document_chunks",
        vector_size: int = 768,
        url: str = settings.QDRANT_URL,
        api_key: Optional[str] = settings.QDRANT_API_KEY,
    ):
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.client = AsyncQdrantClient(url=url, api_key=api_key)

    async def initialize(self):
        try:
            collections_response = await self.client.get_collections()
            collection_names = [c.name for c in collections_response.collections]

            if self.collection_name not in collection_names:
                app_logger.info(f"🚀 Đang tạo Qdrant collection: {self.collection_name}")
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.vector_size,
                        distance=models.Distance.COSINE
                    )
                )

                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="parent_id",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )

                await self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="doc_id",
                    field_schema=models.PayloadSchemaType.KEYWORD,
                )
                app_logger.info("Đã khởi tạo Qdrant và các Payload Indexes.")
        except Exception as e:
            app_logger.error(f"Lỗi khi khởi tạo Qdrant: {e}")
            raise e

    # --- LƯU TRỮ ---
    async def save_children(self, nodes: List[ChildNode]) -> bool:
        if not nodes:
            return True

        points = []
        for node in nodes:
            if not node.embedding:
                app_logger.warning(f"Node {node.id} thiếu embedding, bỏ qua.")
                continue

            doc_id = node.metadata.get("doc_id")
            points.append(
                models.PointStruct(
                    id=str(node.id),
                    vector=node.embedding,
                    payload={
                        "doc_id": str(doc_id) if doc_id else None,
                        "parent_id": str(node.parent_id),
                        "chunk_index": node.chunk_index,
                        "text_chunk": node.text_chunk,
                        "metadata": node.metadata
                    }
                )
            )

        try:
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            return True
        except Exception as e:
            app_logger.error(f"Lỗi khi lưu vectors vào Qdrant: {e}")
            return False

    async def search_vector(
        self,
        query_embedding: List[float],
        top_k: int = 6,
        doc_ids: Optional[List[UUID]] = None,

    ) -> List[ScoredNode]:

        query_filter = None
        if doc_ids:
            doc_ids_str = [str(did) for did in doc_ids]
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="doc_id",
                        match=models.MatchAny(any=doc_ids_str)
                    )
                ]
            )

        try:
            response = await self.client.query_points(
                collection_name=self.collection_name,
                query=cast(Any, query_embedding),
                query_filter=query_filter,
                limit=top_k,
                with_payload=True
            )

            nodes = []
            for hit in response.points:
                payload = hit.payload or {}
                child = ChildNode(
                    id=UUID(str(hit.id)),
                    parent_id=UUID(payload.get("parent_id")),
                    chunk_index=payload.get("chunk_index", 0),
                    text_chunk=payload.get("text_chunk", ""),
                    metadata=payload.get("metadata", {})
                )
                nodes.append(ScoredNode(node=child, score=hit.score))

            return nodes

        except Exception as e:
            app_logger.error(f"Lỗi khi tìm kiếm vector trong Qdrant: {e}")
            return []

    # --- XÓA DỮ LIỆU ---
    async def delete_children_by_parent_ids(self, parent_ids: List[UUID]) -> bool:
        """Xóa theo danh sách parent_id (các đoạn 1200 từ)."""
        if not parent_ids:
            return True

        parent_ids_str = [str(pid) for pid in parent_ids]
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="parent_id",
                            match=models.MatchAny(any=parent_ids_str)
                        )
                    ]
                )
            )
            return True
        except Exception as e:
            app_logger.error(f"Lỗi khi xóa vectors theo parent_ids: {e}")
            return False

    async def delete_children_by_doc_id(self, doc_id: UUID) -> bool:
        """Xóa sạch mọi chunk thuộc về 1 file (doc_id)."""
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="doc_id",
                            match=models.MatchValue(value=str(doc_id))
                        )
                    ]
                )
            )
            return True
        except Exception as e:
            app_logger.error(f"❌ Lỗi khi xóa vectors theo doc_id: {e}")
            return False
