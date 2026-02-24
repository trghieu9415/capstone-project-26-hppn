from typing import List
from sqlalchemy import Column, String, Text, create_engine
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy.orm import declarative_base, sessionmaker

from infrastructure.storage.base import IDocumentStore
from schemas.document import ParentNode

Base = declarative_base()


class ParentDocumentEntity(Base):
    __tablename__ = "parent_documents"

    id = Column(String(255), primary_key=True)
    full_text = Column(Text, nullable=False)
    document_metadata = Column("metadata", JSONB, default=dict)


class PostgresAdapter(IDocumentStore):
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string, pool_pre_ping=True)

        Base.metadata.create_all(self.engine)

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def save_parents(self, nodes: List[ParentNode]) -> bool:
        if not nodes:
            return True

        try:
            with self.SessionLocal() as session:
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

                    session.execute(update_stmt)

                session.commit()
            return True
        except Exception as e:
            print(f"[Error] Lỗi khi lưu Parent Nodes bằng SQLAlchemy: {e}")
            return False

    def get_parents_by_ids(self, parent_ids: List[str]) -> List[ParentNode]:
        if not parent_ids:
            return []

        results = []
        try:
            with self.SessionLocal() as session:
                entities = (
                    session.query(ParentDocumentEntity)
                    .filter(ParentDocumentEntity.id.in_(parent_ids))
                    .all()
                )

                for entity in entities:
                    node = ParentNode(
                        id=entity.id,
                        full_text=entity.full_text,
                        metadata=(
                            entity.document_metadata if entity.document_metadata else {}
                        ),
                    )
                    results.append(node)

            return results
        except Exception as e:
            print(f"[Error] Lỗi khi truy vấn Parent Nodes bằng SQLAlchemy: {e}")
            return []
