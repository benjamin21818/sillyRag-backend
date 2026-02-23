from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class ChunkEmbeddingDTO(BaseModel):

    chunk_id: UUID
    space_id: Optional[UUID]
    file_id: Optional[UUID]
    file_name: Optional[str]
    context: Optional[str]


    model_config = {
        'from_attributes': True
    }