from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.pg_db import get_db
from src.services.user_service import UserService
from datetime import datetime
import uuid
from src.utils.api_contract import APIContract
from src.utils.logger import get_logger
logger = get_logger(__name__)



router = APIRouter(
    prefix="/user",
    tags=["user"],
)

# 增
@router.post("/create")
async def create(data: dict, session: AsyncSession = Depends(get_db)):
    service = UserService(session)
    instance =  await service.create(
        id=uuid.uuid4(),
        name=data.get('name'),
        password=data.get('password'),
        openai_api_key=data.get('openai_api_key'),
        openai_api_base=data.get('openai_api_base'),
        deepseek_api_key=data.get('deepseek_api_key'),
        llm_model=data.get('llm_model'),
        temperature=data.get('temperature'),
        prompt_system=data.get('prompt_system'),
        prompt_system_rag=data.get('prompt_system_rag'),
        search_mode=data.get('search_mode'),
        top_n=data.get('top_n'),
        threshold_vector=data.get('threshold_vector'),
        threshold_fulltext=data.get('threshold_fulltext'),
        created_at=datetime.now()
    )
    logger.info(f"创建用户成功: {data}")
    return APIContract.success(instance)

# 删
@router.delete("/delete/{id}")
async def delete(id: str, session: AsyncSession = Depends(get_db)):
    service = UserService(session)
    instance = await service.delete_by_primary_key(id)
    logger.info(f"删除用户成功: {id}")
    return APIContract.success(instance)

# 改
@router.put("/update/{id}")
async def update(id: str, data: dict, session: AsyncSession = Depends(get_db)):
    service = UserService(session)
    # 允许更新的字段列表
    allowed_fields = [
        'name', 'password', 'openai_api_key', 'openai_api_base',
        'deepseek_api_key', 'llm_model', 'temperature', 'prompt_system',
        'prompt_system_rag', 'search_mode', 'top_n', 'threshold_vector',
        'threshold_fulltext'
    ]
    # 过滤掉 data 中值为 None 的项以及不在 allowed_fields 中的项
    update_data = {
        k: v for k, v in data.items() 
        if k in allowed_fields and v is not None
    }
    instance = await service.update_by_primary_key(id, **update_data)
    logger.info(f"更新用户成功: {id}")
    return APIContract.success(instance)

# 查
@router.get("/get/{id}")
async def get(id: str, session: AsyncSession = Depends(get_db)):
    service = UserService(session)
    instance = await service.get_by_primary_key(id)
    logger.info(f"查询用户成功: {id}")
    return APIContract.success(instance)
@router.get("/get_all")
async def get_all(session: AsyncSession = Depends(get_db)):
    service = UserService(session)
    instances = await service.get_all()
    logger.info(f"查询所有用户成功")
    return APIContract.success(instances)
