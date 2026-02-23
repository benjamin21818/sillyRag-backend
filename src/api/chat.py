from fastapi import APIRouter,Depends
from src.utils.api_contract import APIContract
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.pg_db import get_db
from pydantic import BaseModel
from src.handler.chat.chat_handler import ChatModelHandler
from src.handler.chat.history_handler import ChatHistoryHandler
from src.utils.logger import get_logger

logger = get_logger(__name__)



router = APIRouter(
    tags=["chat"],
    prefix="/chat"
)


class ChatRequest(BaseModel):
    user_id:str
    message:str
    llm_model:str
    space_id:str = None

@router.post("/type")
async def chat_with_user(req:ChatRequest,session: AsyncSession = Depends(get_db)):

    if req.space_id:
        response = await ChatModelHandler().get_llm_response(req.user_id,req.message,req.llm_model,req.space_id)
    else:
        response = await ChatModelHandler().get_llm_response(req.user_id,req.message,req.llm_model)
    
    if response:
        return APIContract.success(response)
    else:
        return APIContract.error(500, "获取模型会话失败")


@router.get("/history")
async def get_user_chat_history(user_id:str,space_id:str = None):
    history = await ChatHistoryHandler().get_user_chat_messages(user_id,space_id)
    if history:
        return APIContract.success(history)
    else:
        return APIContract.error(500, "获取聊天记录失败")



@router.delete("/clear_history")
async def clear_user_chat_history(user_id:str,space_id:str = None):
    await ChatHistoryHandler().clear_user_chat_history(user_id,space_id)
    return APIContract.success({"message":"清空成功！"})
