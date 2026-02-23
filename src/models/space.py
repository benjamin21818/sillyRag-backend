from src.models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, VARCHAR, JSON




class Space(Base):
    __tablename__ = "space"
    uuid = Column(UUID, primary_key=True, index=True)
    name = Column(VARCHAR)
    create_time = Column(TIMESTAMP(timezone=True),nullable=False)

    files = relationship("File", back_populates="space")
    embeddings = relationship("Embedding", back_populates="space")
