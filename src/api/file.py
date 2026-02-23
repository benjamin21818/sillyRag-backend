import uuid
from fastapi import APIRouter, Depends, UploadFile, Form, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.pg_db import get_db
from src.services import chunk_service
from src.services.file_service import FileService
from src.services.chunk_service import ChunkService
from src.services.embedding_service import EmbeddingService
import os
from src.utils.api_contract import APIContract
from datetime import datetime
from dotenv import load_dotenv
from src.utils.conf import PROJECT_DIR
load_dotenv(os.path.join(PROJECT_DIR, ".env"))
from src.utils.logger import get_logger
logger = get_logger(__name__)



router = APIRouter(
    prefix="/file",
    tags=["file"],
)


# 增
@router.post("/upload")
async def upload_file(file: UploadFile = File(...), space_id: str = Form(...), session: AsyncSession = Depends(get_db)):
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["txt", "pdf", "docx","md","csv"]:
        return APIContract.error(400, "仅支持上传txt、pdf、docx、md、csv文件")

    # 保存文件到本地
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    save_path = os.path.join(upload_dir, file.filename)
    try:
        with open(save_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        logger.error(f"上传文件失败: {file.filename}, 错误信息: {str(e)}")
        return APIContract.error(500, "上传文件失败")

    # 文件数据库添加记录
    service = FileService(session)
    file_dto = await service.create(
        uuid=uuid.uuid4(), 
        space_id=uuid.UUID(space_id), 
        file_name=file.filename, 
        file_extension=file_extension,
        create_time=datetime.now(),
        status=0
        )
    logger.info(f"上传文件成功: {file.filename}")

    return APIContract.success({"filename":file.filename,"message":"文件上传成功，后台分块处理中！"})


    
# 删
@router.delete("/delete/{uuid}")
async def delete_file(uuid:str,session:AsyncSession=Depends(get_db)):
    file_service = FileService(session)
    await file_service.delete_by_primary_key(uuid)
    chunk_service = ChunkService(session)
    await chunk_service.delete_chunks_by_file_id(uuid)
    embedding_service = EmbeddingService(session)
    await embedding_service.delete_embeddings_by_file_id(uuid)
    return APIContract.success({"message":"文件、文件块、向量均成功删除！"})



# 查
@router.get("/get_by_space_id/{space_id}")
async def get_files_by_space_id(space_id:str,session:AsyncSession=Depends(get_db)):
    file_service = FileService(session)
    files = await file_service.get_files_by_space_id(space_id)
    if files:
        return APIContract.success(files)
    return APIContract.success({"message":"暂无文件！"})

@router.get("/get_all")
async def get_all_files(session:AsyncSession=Depends(get_db)):
    file_service = FileService(session)
    files = await file_service.get_all()
    if files:
        return APIContract.success(files)
    return APIContract.success({"message":"暂无文件！"})


    
