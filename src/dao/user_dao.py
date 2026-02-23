from src.dao.base_dao import BaseDao
from src.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession



class UserDao(BaseDao):
    def __init__(self,session: AsyncSession):
        super().__init__(session,User,primary_key='id')
