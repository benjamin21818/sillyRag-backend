from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from src.db.pg_db import get_db
from src.services.user_service import UserService
from src.core.llm.deepseek_llm import DeepSeekLLM
from src.core.llm.openai_llm import OpenAILLM
from src.core.prompts.rag_prompt import RAGPrompt
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_postgres import PostgresChatMessageHistory
from src.handler.search.vector_search_chunk import VectorSearchChunk
from src.handler.search.fulltext_search_chunk import FulltextSearchChunk
from src.handler.search.reranker import Reranker
import asyncio
from src.services.chunk_service import ChunkService
from src.db.pg_db import create_async_connection
from src.utils.logger import get_logger
import uuid
logger = get_logger(__name__)


class ChatModelHandler:
    def __init__(self):
        pass


    # 初始化大模型
    async def init_llm_response(self,user,llm_model:str):
        if llm_model == "deepseek":
            llm = await DeepSeekLLM().init_llm_model(user)
        elif llm_model == "openai":
            llm = await OpenAILLM().init_llm_model(user)
        return llm


    # 用提示词模版、记忆模块、llm组成chain
    async def init_chain(self,user,llm_model:str,space_id:str = None):
            llm = await self.init_llm_response(user,llm_model)
            prompt = await RAGPrompt().init_chat_prompt(user,space_id)
            chain = prompt | llm

            async_connection = await create_async_connection()
            chain_with_history = RunnableWithMessageHistory(
                chain,
                lambda session_id: PostgresChatMessageHistory(
                    "user_history",
                    session_id,
                    async_connection=async_connection
                ),
                input_messages_key="question",
                history_messages_key="history",
            )
            return chain_with_history





    async def _get_chunks_by_space_id(self,message:str,search_mode:str,top_n:int,threshold_vector:float,threshold_fulltext:float,space_id:str):
        if search_mode == "vector":
            chunk_ids = await VectorSearchChunk().vector_search_chunk(message,top_n,threshold_vector,space_id)
            return chunk_ids
        elif search_mode == "fulltext":
            chunk_ids = await FulltextSearchChunk().fulltext_search_chunk(message,top_n,threshold_fulltext,space_id)
            return chunk_ids
        elif search_mode == "hybrid":
            vec_chunk_ids,fulltext_chunk_ids = await asyncio.gather(
                VectorSearchChunk().vector_search_chunk(message,top_n,threshold_vector,space_id),
                FulltextSearchChunk().fulltext_search_chunk(message,top_n,threshold_fulltext,space_id)
            )
            # 使用 dict.fromkeys 保持顺序，[:top_n] 确保最终数量符合预期
            chunk_ids = list(dict.fromkeys(vec_chunk_ids + fulltext_chunk_ids))[:top_n]
            chunk_ids = await Reranker().rerank(message,chunk_ids,top_n)
            return chunk_ids
        




    async def get_llm_response(self,user_id:str,message:str,llm_model:str,space_id:str = None):
         async for session in get_db():
            try:
                user_service = UserService(session)
                user = await user_service.get_by_primary_key(user_id)
                chain = await self.init_chain(user,llm_model,space_id)

                search_mode = user.search_mode if user.search_mode else "hybrid"                  # 检索模式
                top_n = user.top_n if user.top_n else 3                                           # Top-N
                threshold_vector = user.threshold_vector if user.threshold_vector else 0.7        # 向量搜索阈值
                threshold_fulltext = user.threshold_fulltext if user.threshold_fulltext else 0.5  # 全文搜索阈值

                # 构造 session_id，如果存在 space_id 则联合 user_id 使用，实现空间隔离的记忆
                if space_id:
                    session_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}_{space_id}"))
                else:
                    session_id = user_id
                
                config = {"configurable": {"session_id": session_id}}
                result = {}

                if space_id:
                    logger.info(f"使用RAG模式。。。session_id: {session_id}")
                    reranked_chunk_ids = await self._get_chunks_by_space_id(message,search_mode,top_n,threshold_vector,threshold_fulltext,space_id)
                    chunks = []
                    if reranked_chunk_ids:
                        chunks = await ChunkService(session).get_chunks_by_primary_keys(reranked_chunk_ids)
                        chunks = [doc.context for doc in chunks] if chunks else []
                    
                    context_str = "\n".join(chunks) if chunks else ""
                    response = await chain.ainvoke({"question":message,"context":context_str},config=config)      
                    if isinstance(response,AIMessage):
                        result["content"] = response.content
                    else:
                        raise ValueError("返回的不是AIMessage")
                    return result
                else:
                    logger.info(f"使用普通模式。。。session_id: {session_id}")
                    response = await chain.ainvoke({"question":message},config=config)
                    if isinstance(response,AIMessage):
                        result["content"] = response.content
                    else:
                        raise ValueError("返回的不是AIMessage")
                    return result
            finally:
                pass # get_db 会自动关闭 session





