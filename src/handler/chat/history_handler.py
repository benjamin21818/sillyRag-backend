from langchain_postgres import PostgresChatMessageHistory
from src.db.pg_db import create_async_connection
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid


class ChatHistoryHandler:

    def __init__(self):
        self.chat_history = {}



    #文本聊天记录
    async def get_user_chat_history(self, user_id: str, space_id: str = None):
        if space_id:
            session_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id}_{space_id}"))
        else:
            session_id = user_id
            
        if self.chat_history.get(session_id):
            return self.chat_history[session_id]
        else:
            async_connection = await create_async_connection()
            self.chat_history[session_id] = PostgresChatMessageHistory(
                "user_history",
                session_id,
                async_connection=async_connection,
            )
            return self.chat_history[session_id]


    async def get_user_chat_messages(self,user_id,space_id: str = None):
        history = await self.get_user_chat_history(user_id,space_id)
        messages = await history.aget_messages()
        if messages is None or len(messages) == 0:
            return []
        return messages


    async def clear_user_chat_history(self,user_id,space_id: str = None):
        history = await self.get_user_chat_history(user_id,space_id)
        await history.aclear()








