from src.services.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from src.dto.user_dto import UserDTO
from src.dao.user_dao import UserDao


class UserService(BaseService):
    def __init__(self,session:AsyncSession):
        super().__init__(UserDao(session),UserDTO)