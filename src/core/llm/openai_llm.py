from src.core.llm.base_llm import BaseLLM
from langchain_openai import ChatOpenAI
from src.services.user_service import UserService
from src.db.pg_db import get_db
import asyncio
from src.utils.logger import get_logger
logger = get_logger(__name__)



class OpenAILLM(BaseLLM):
    def __init__(self):
        self.llm = None

    async def init_llm_model(self,user):
        
        api_key = user.openai_api_key if user.openai_api_key else None
        base_url = user.openai_api_base if user.openai_api_base else None
        temperature = user.temperature if user.temperature else 0.5

        if api_key and base_url:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=api_key,
                base_url=base_url,
                temperature=temperature,
            )
        else:
            logger.error("OpenAI API key or base URL not found")
            
        return self.llm