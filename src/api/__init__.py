from fastapi import APIRouter
from src.api.space import router as space_router
from src.api.user import router as user_router
from src.api.file import router as file_router
from src.api.chunk import router as chunk_router
from src.api.chat import router as chat_router
from src.api.voice import router as voice_router

# 创建主路由，统一管理所有子模块的路由
# 修改前缀为 /api，与用户请求的路径保持一致
router = APIRouter(prefix="/api") 

# 注册子模块路由
router.include_router(space_router)
router.include_router(user_router)
router.include_router(file_router)
router.include_router(chunk_router)
router.include_router(chat_router)
router.include_router(voice_router)

__all__ = ["router"]
