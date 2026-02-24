from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from infrastructure.storage.base import IVectorStore
from schemas.document import ChildNode


class QdrantAdapter(IVectorStore):
    def __init__(
        self, collection_name: str, vector_size: int, path: str = "./data/qdrant_db"
    ):
        self.collection_name = collection_name
        self.client = QdrantClient(path=path)
        self._init_collection(vector_size)

    def _init_collection(self, vector_size: int):

        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def save_children(self, nodes: List[ChildNode]) -> bool:

        if not nodes:
            return True

        points = []
        for node in nodes:
            if not node.embedding:
                print(f"[Warning] Node {node.id} không có embedding, bỏ qua.")
                continue

            payload = {
                "parent_id": node.parent_id,
                "text_chunk": node.text_chunk,
                **node.metadata,
            }

            points.append(
                PointStruct(id=node.id, vector=node.embedding, payload=payload)
            )

        try:
            self.client.upsert(collection_name=self.collection_name, points=points)
            return True
        except Exception as e:
            print(f"[Error] Lỗi lưu vector vào Qdrant: {e}")
            return False

    def search_vector(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[ChildNode]:

        try:
            search_result = self.client.search(
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
            print(f"[Error] Lỗi khi query Qdrant: {e}")
            return []
