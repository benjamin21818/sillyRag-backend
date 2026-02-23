from src.dao.base_dao import BaseDao
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.files import File
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class FileDao(BaseDao):
    def __init__(self, session: AsyncSession):
        super().__init__(session, File)

    async def get_files_by_space_id(self, space_id):
        # 构造查询语句：查询 File 表，条件是 space_id 匹配
        # options(joinedload(File.space)) 表示连表查询 Space 信息，如果不加这一行，file.space 属性默认是延迟加载的
        stmt = select(File).where(File.space_id == space_id).options(joinedload(File.space))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_files_by_status(self, status: int):
        stmt = select(File).where(File.status == status)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
