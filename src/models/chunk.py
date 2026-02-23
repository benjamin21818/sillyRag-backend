from src.models.base import Base
from sqlalchemy import Column, INTEGER, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, VARCHAR


class Chunk(Base):
    __tablename__ = "chunk"
    uuid = Column(UUID, primary_key=True, index=True)
    file_id = Column(UUID, ForeignKey("file.uuid"))
    file_name = Column(VARCHAR)
    context = Column(VARCHAR)
    index = Column(INTEGER)
    status = Column(INTEGER)
    create_time = Column(TIMESTAMP(timezone=True),nullable=False)

    file = relationship("File", back_populates="chunks")
    embeddings = relationship("Embedding", back_populates="chunk")

