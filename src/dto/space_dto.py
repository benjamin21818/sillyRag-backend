from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class SpaceDTO(BaseModel):
    uuid: UUID
    name: Optional[str]
    create_time: datetime

    model_config = {
        'from_attributes': True
    }