from src.core.llm.base_llm import BaseLLM
from langchain_deepseek import ChatDeepSeek
from src.services.user_service import UserService
from src.db.pg_db import get_db
import asyncio
from src.utils.logger import get_logger
logger = get_logger(__name__)



class DeepSeekLLM(BaseLLM):
    def __init__(self):
        self.llm = None

    async def init_llm_model(self,user):
       
        api_key = user.deepseek_api_key if user.deepseek_api_key else None
        temperature = user.temperature if user.temperature else 0.5

        if api_key:
            self.llm = ChatDeepSeek(
                model='deepseek-chat',
                api_key=api_key,
                temperature=temperature,
            )
        else:
            logger.error("Deepseek API key not found")
        return self.llm



# if __name__ == "__main__":
#     asyncio.run(DeepSeekLLM().init_llm_model(user_id="db657a21-db1a-4422-8e88-1e88750147e1"))
