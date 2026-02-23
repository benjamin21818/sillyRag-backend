from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.pg_db import get_db
from src.utils.api_contract import APIContract
from src.handler.voice.voice_handler import VoiceHandler
from src.handler.voice.voice_history_handler import VoiceHistoryHandler
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    tags=["voice"],
    prefix="/voice"
)


@router.post("/voice")
async def chat_with_voice(
    user_id: str = Form(...),
    llm_model: str = Form(None),
    space_id: str = Form(None),
    audio: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
):
    try:
        handler = VoiceHandler()
        result = await handler.handle_voice_chat(
            file=audio,
            user_id=user_id,
            llm_model=llm_model,
            space_id=space_id,
            session=session
        )
        
        if result:
            return APIContract.success(result)
        else:
            return APIContract.error(500, "语音会话处理失败")
    except Exception as e:
        logger.error(f"Error in chat_with_user voice: {e}")
        return APIContract.error(500, f"语音服务异常: {str(e)}")


@router.get("/history")
async def get_user_voice_history(
    user_id: str,
    space_id: str = None,
    session: AsyncSession = Depends(get_db),
):
    history = await VoiceHistoryHandler().get_voice_history(session, user_id, space_id)
    return APIContract.success(history)


@router.delete("/clear_history")
async def clear_user_voice_history(
    user_id: str,
    space_id: str = None,
    session: AsyncSession = Depends(get_db),
):
    await VoiceHistoryHandler().clear_voice_history(session, user_id, space_id)
    return APIContract.success({"message":"清空成功！"})
