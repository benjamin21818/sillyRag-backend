from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from pgvector.utils import Vector

class EmbeddingDTO(BaseModel):
    uuid: UUID
    space_id: Optional[UUID]
    file_id: Optional[UUID]
    chunk_id: Optional[UUID]
    embedding_vector: Vector
    search_vector: Optional[str]
    create_time: datetime
    
    model_config = {
        'from_attributes': True,
        'arbitrary_types_allowed': True
    }