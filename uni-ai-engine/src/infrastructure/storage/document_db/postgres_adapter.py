from typing import List
from sqlalchemy import Column, String, Text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select

from infrastructure.storage.base import IDocumentStore
from schemas.document import ParentNode
from utils.logger import app_logger

Base = declarative_base()


class ParentDocumentEntity(Base):
    __tablename__ = "parent_documents"
    id = Column(String(255), primary_key=True)
    full_text = Column(Text, nullable=False)
    document_metadata = Column("metadata", JSONB, default=dict)


class PostgresAdapter(IDocumentStore):
    def __init__(self, connection_string: str):
        self.engine = create_async_engine(connection_string, pool_pre_ping=True)
        self.SessionLocal = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def save_parents(self, nodes: List[ParentNode]) -> bool:
        if not nodes:
            return True
        try:
            async with self.SessionLocal() as session:
                for node in nodes:
                    stmt = insert(ParentDocumentEntity).values(
                        id=node.id,
                        full_text=node.full_text,
                        document_metadata=node.metadata,
                    )
                    update_stmt = stmt.on_conflict_do_update(
                        index_elements=["id"],
                        set_=dict(
                            full_text=stmt.excluded.full_text,
                            document_metadata=stmt.excluded.document_metadata,
                        ),
                    )
                    await session.execute(update_stmt)
                await session.commit()
            return True
        except Exception as e:
            app_logger.error(f"Lỗi khi lưu Parent Nodes: {e}")
            return False

    async def get_parents_by_ids(self, parent_ids: List[str]) -> List[ParentNode]:
        if not parent_ids:
            return []
        results = []
        try:
            async with self.SessionLocal() as session:
                stmt = select(ParentDocumentEntity).where(
                    ParentDocumentEntity.id.in_(parent_ids)
                )
                result = await session.execute(stmt)
                entities = result.scalars().all()

                for entity in entities:
                    results.append(
                        ParentNode(
                            id=entity.id,
                            full_text=entity.full_text,
                            metadata=(
                                entity.document_metadata
                                if entity.document_metadata
                                else {}
                            ),
                        )
                    )
            return results
        except Exception as e:
            app_logger.error(f"Lỗi khi truy vấn Parent Nodes: {e}")
            return []
