from fastapi import Depends,APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.space_service import SpaceService
from src.db.pg_db import get_db
import uuid
from datetime import datetime



router = APIRouter(
    prefix="/space",
    tags=["space"],
)


# 增
@router.post("/create")
async def create(data: dict, session: AsyncSession = Depends(get_db)):
    service = SpaceService(session)
    return await service.create(uuid=uuid.uuid4(),name=data['name'],create_time=datetime.now())


# 删
@router.delete("/delete/{uuid}")
async def delete(uuid: str, session: AsyncSession = Depends(get_db)):
    service = SpaceService(session)
    # 调用时直接传入位置参数，而不是关键字参数 uuid=uuid
    return await service.delete_by_primary_key(uuid)

# 改
@router.put("/update/{uuid}")
async def update(uuid: str, data: dict, session: AsyncSession = Depends(get_db)):
    service = SpaceService(session)
    # 调用时直接传入位置参数，而不是关键字参数 uuid=uuid
    return await service.update_by_primary_key(uuid, name=data['name'])

# 查
@router.get("/get/{uuid}")
async def get(uuid: str, session: AsyncSession = Depends(get_db)):
    service = SpaceService(session)
    return await service.get_by_primary_key(uuid)
@router.get("/get_all")
async def get_all(session: AsyncSession = Depends(get_db)):
    service = SpaceService(session)
    return await service.get_all()
