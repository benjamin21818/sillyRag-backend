from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional



class UserDTO(BaseModel):
    id: UUID
    name: Optional[str]
    password: Optional[str]
    openai_api_key: Optional[str]
    openai_api_base: Optional[str]
    deepseek_api_key: Optional[str]
    llm_model: Optional[str]
    temperature: Optional[float]
    prompt_system: Optional[str]
    prompt_system_rag: Optional[str]
    search_mode: Optional[str]
    top_n: Optional[int]
    threshold_vector: Optional[float]
    threshold_fulltext: Optional[float]
    created_at: datetime

    model_config = {
        'from_attributes': True
    }