from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.chunk_service import ChunkService
from src.utils.api_contract import APIContract
from src.db.pg_db import get_db
from src.utils.logger import get_logger
logger = get_logger(__name__)


router = APIRouter(
    tags=["chunk"],
    prefix="/chunk"
)

@router.get("/file/{file_id}")
async def get_chunks_by_file_id(file_id:str,session:AsyncSession = Depends(get_db)):
    chunk_service = ChunkService(session)
    chunks = await chunk_service.get_chunks_by_file_id(file_id)
    if chunks:
        return APIContract.success(chunks)
    return APIContract.success({"message":"暂无文件块！"})
