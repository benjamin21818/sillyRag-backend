from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel



class ChunkDTO(BaseModel):
    uuid: UUID
    file_id: UUID
    file_name: Optional[str]
    context: Optional[str]
    index: Optional[int]
    status: Optional[int]
    create_time: datetime

    model_config = {
        'from_attributes': True
    }
