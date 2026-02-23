from src.dao.file_dao import FileDao
from src.services.base_service import BaseService
from src.dto.file_dto import FileDTO
from sqlalchemy.ext.asyncio import AsyncSession


class FileService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(FileDao(session), FileDTO)
        self.dao: FileDao = self.dao


    async def get_files_by_space_id(self, space_id: str):
        results = await self.dao.get_files_by_space_id(space_id)
        if results:
            return [FileDTO.model_validate(result) for result in results]
        return None

    async def get_files_by_status(self, status: int):
        results = await self.dao.get_files_by_status(status)
        if results:
            return [FileDTO.model_validate(result) for result in results]
        return None
