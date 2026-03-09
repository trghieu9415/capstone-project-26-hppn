from typing import List
from uuid import UUID
from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from infrastructure.storage.base import IDocumentStore
from schemas.document import ParentNode

Base = declarative_base()


class ParentDocumentModel(Base):
    __tablename__ = "parent_documents"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    full_text = Column(Text, nullable=False)
    metadata_col = Column("metadata", JSONB, default=dict, nullable=False)


class PostgresDocumentStore(IDocumentStore):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def save_parents(self, nodes: List[ParentNode]) -> bool:
        if not nodes:
            return True

        async with self.session_factory() as session:
            try:
                values = [
                    {
                        "id": node.id,
                        "full_text": node.full_text,
                        "metadata": node.metadata
                    }
                    for node in nodes
                ]

                stmt = insert(ParentDocumentModel).values(values)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id'],
                    set_={
                        "full_text": stmt.excluded.full_text,
                        "metadata": stmt.excluded.metadata
                    }
                )

                await session.execute(stmt)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                print(f"Error saving parent documents: {e}")
                return False

    async def get_parents_by_ids(self, parent_ids: List[UUID]) -> List[ParentNode]:
        if not parent_ids:
            return []

        async with self.session_factory() as session:
            stmt = select(ParentDocumentModel).where(
                ParentDocumentModel.id.in_(parent_ids)
            )
            result = await session.execute(stmt)
            records = result.scalars().all()

            return [
                ParentNode(
                    id=record.id,
                    full_text=record.full_text,
                    metadata=record.metadata_col
                )
                for record in records
            ]

    async def delete_parents(self, parent_ids: List[UUID]) -> bool:
        if not parent_ids:
            return True

        async with self.session_factory() as session:
            try:
                stmt = delete(ParentDocumentModel).where(
                    ParentDocumentModel.id.in_(parent_ids))
                await session.execute(stmt)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                print(f"Error deleting parent documents: {e}")
                return False
