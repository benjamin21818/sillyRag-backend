from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import history


from src.utils.logger import get_logger
logger = get_logger(__name__)



class RAGPrompt:
    def __init__(self):
        pass


    async def init_chat_prompt(self,user,space_id:str = None):
        if space_id:
            logger.info("使用RAG模式提示词。。。")
            user_prompt = user.prompt_system_rag
            prompt = ChatPromptTemplate.from_messages([
                ("system", user_prompt),
                ("human", "历史对话：{history},\n用户文档：{context}\n,请严格根据用户的文档回答用户的问题：\n{question}"),
            ])
            return prompt
        else:
            logger.info("使用直接交互提示词。。。")
            user_prompt = user.prompt_system
            prompt = ChatPromptTemplate.from_messages([
                ("system", user_prompt),
                ("human", "{question}"),
            ])
            return prompt



    async def init_voice_prompt(self,user,space_id:str = None):
        if space_id:
            logger.info("使用RAG模式提示词。。。")
            user_prompt = user.prompt_system_rag
            prompt = ChatPromptTemplate.from_messages([
                ("system", user_prompt),
                ("human", "\n用户文档：{context}\n,请严格根据用户的文档回答用户的问题：\n{question}"),
            ])
            return prompt
        else:
            logger.info("使用直接交互提示词。。。")
            user_prompt = user.prompt_system
            prompt = ChatPromptTemplate.from_messages([
                ("system", user_prompt),
                ("human", "{question}"),
            ])
            return prompt