from src.dao.base_dao import BaseDao
from src.models.space import Space
from sqlalchemy.ext.asyncio import AsyncSession

class SpaceDao(BaseDao):
    def __init__(self,session: AsyncSession):
        super().__init__(session,Space)