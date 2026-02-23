from src.models.base import Base
from sqlalchemy import Column, INTEGER, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, VARCHAR, JSON, TSVECTOR
from pgvector.sqlalchemy import Vector


class Embedding(Base):
    __tablename__ = "embedding"
    uuid = Column(UUID, primary_key=True, index=True)
    space_id = Column(UUID, ForeignKey("space.uuid"))
    file_id = Column(UUID, ForeignKey("file.uuid"))
    chunk_id = Column(UUID, ForeignKey("chunk.uuid"))
    embedding_vector = Column(Vector)
    search_vector = Column(TSVECTOR)
    create_time = Column(TIMESTAMP(timezone=True),nullable=False)

    space = relationship("Space", back_populates="embeddings")
    file = relationship("File", back_populates="embeddings")
    chunk = relationship("Chunk", back_populates="embeddings")