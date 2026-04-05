from typing import List, Dict
from uuid import UUID
from sqlalchemy import Column, Text, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert

from infrastructure.storage.base import IDocumentStore
from schemas.document import ParentNode
from utils.loggers.app_logger import app_logger


class Base(DeclarativeBase):
    pass


class DocumentModel(Base):
    __tablename__ = "documents"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    extension = Column(String, nullable=False)


class ParentDocumentModel(Base):
    __tablename__ = "parent_documents"
    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    doc_id = Column(PG_UUID(as_uuid=True), index=True, nullable=False)
    full_text = Column(Text, nullable=False)
    extra_data = Column("extra_data", JSONB, default=dict, nullable=False)


class PostgresDocumentStore(IDocumentStore):
    async def get_parent_ids_by_doc_id(self, doc_id: UUID) -> List[UUID]:
        if not doc_id:
            return []

        async with self.session_factory() as session:
            try:
                stmt = select(ParentDocumentModel.id).where(
                    ParentDocumentModel.doc_id == doc_id
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
            except Exception as e:
                app_logger.error(
                    f"Lỗi khi lấy danh sách parent IDs cho doc_id {doc_id}: {e}")
                return []

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
                        "doc_id": node.doc_id,
                        "full_text": node.full_text,
                        "extra_data": node.metadata
                    }
                    for node in nodes
                ]

                stmt = insert(ParentDocumentModel).values(values)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['id'],
                    set_={
                        "full_text": stmt.excluded.full_text,
                        "doc_id": stmt.excluded.doc_id,
                        "extra_data": stmt.excluded.extra_data
                    }
                )

                await session.execute(stmt)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                app_logger.error(f"Error saving parent documents: {e}")
                raise e

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
                    doc_id=record.doc_id,
                    full_text=record.full_text,
                    metadata=record.extra_data
                )
                for record in records
            ]

    async def get_doc_names_by_parent_ids(
        self,
        parent_ids: List[UUID]
    ) -> Dict[UUID, str]:
        if not parent_ids:
            return {}

        async with self.session_factory() as session:
            try:
                stmt = (
                    select(
                        ParentDocumentModel.id,
                        DocumentModel.name,
                        DocumentModel.extension,
                        ParentDocumentModel.extra_data["chunk_index"]
                    )
                    .join(DocumentModel, ParentDocumentModel.doc_id == DocumentModel.id)
                    .where(ParentDocumentModel.id.in_(parent_ids))
                    .distinct()
                )

                result = await session.execute(stmt)
                records = result.all()

                formatted_records = "\n".join(
                    f"  + Parent ID: {r[0]} | Tên file: {r[1]}{r[2]} | Chunk: {r[3]}"
                    for r in records
                )
                app_logger.info(f"Danh sách Tài liệu được chọn:\n{formatted_records}")

                return {record.id: f"{record.name}{record.extension}"
                        for record in records}

            except Exception as e:
                app_logger.error(
                    f"Lỗi khi lấy danh sách tên document từ parent_ids: {e}")
                raise e

    async def delete_parents(self, doc_ids: List[UUID]) -> bool:
        if not doc_ids:
            return True

        async with self.session_factory() as session:
            try:
                stmt = delete(ParentDocumentModel).where(
                    ParentDocumentModel.doc_id.in_(doc_ids))
                await session.execute(stmt)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                app_logger.error(f"Lỗi khi xóa parent documents: {e}")
                raise e
