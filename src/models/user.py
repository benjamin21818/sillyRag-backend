from src.models.base import Base
from sqlalchemy import Column, INTEGER, FLOAT, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, VARCHAR


class User(Base):
    __tablename__ = "user"
    id = Column(UUID, primary_key=True, index=True)
    name = Column(VARCHAR)
    password = Column(VARCHAR)
    openai_api_key = Column(VARCHAR)
    openai_api_base = Column(VARCHAR)
    deepseek_api_key = Column(VARCHAR)
    llm_model = Column(VARCHAR)
    temperature = Column(FLOAT)
    prompt_system = Column(VARCHAR)
    prompt_system_rag = Column(VARCHAR)
    search_mode = Column(VARCHAR)
    top_n = Column(INTEGER)
    threshold_vector = Column(FLOAT)
    threshold_fulltext = Column(FLOAT)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
