from src.models.base import Base
from sqlalchemy import Column, ForeignKey, TIMESTAMP, INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, VARCHAR


class File(Base):
    __tablename__ = "file"
    uuid = Column(UUID, primary_key=True, index=True)
    space_id = Column(UUID, ForeignKey("space.uuid"))
    file_name = Column(VARCHAR)
    file_extension = Column(VARCHAR)
    create_time = Column(TIMESTAMP(timezone=True),nullable=False)
    status = Column(INTEGER)

    space = relationship("Space", back_populates="files")
    chunks = relationship("Chunk", back_populates="file")
    embeddings = relationship("Embedding", back_populates="file")
