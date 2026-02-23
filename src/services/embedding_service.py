from uuid import UUID
from src.services.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from src.dto.embedding_dto import EmbeddingDTO
from src.dao.embedding_dao import EmbeddingDao


class EmbeddingService(BaseService):
    def __init__(self,session:AsyncSession):
        super().__init__(EmbeddingDao(session),EmbeddingDTO)
        self.dao: EmbeddingDao = self.dao


    # 进行批量向量化
    async def batch_create_embeddings(self, items: list) -> None:
        return await self.dao.batch_create_embeddings(items)

    # 通过文件id删除向量
    async def delete_embeddings_by_file_id(self, file_id: UUID) -> None:
        return await self.dao.delete_embeddings_by_file_id(file_id)


    