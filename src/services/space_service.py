from src.services.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from src.dto.space_dto import SpaceDTO
from src.dao.space_dao import SpaceDao


class SpaceService(BaseService):
    def __init__(self,session:AsyncSession):
        super().__init__(SpaceDao(session),SpaceDTO)