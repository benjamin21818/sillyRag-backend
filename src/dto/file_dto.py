from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class FileDTO(BaseModel):
    uuid: UUID
    space_id: UUID
    file_name: Optional[str]
    file_extension: Optional[str]
    create_time: datetime
    status: Optional[int]
    
    model_config = {
        'from_attributes': True
    }
