from src.services.base_service import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from src.dto.chunk_dto import ChunkDTO
from src.dto.chunk_embedding_dto import ChunkEmbeddingDTO
from src.dao.chunk_dao import ChunkDao



class ChunkService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(ChunkDao(session), ChunkDTO)
        self.dao: ChunkDao = self.dao


    # 根据file_id获取chunks
    async def get_chunks_by_file_id(self, file_id: str) -> list[ChunkDTO]:
        chunks = await self.dao.get_by_file_id(file_id)
        if chunks:
            return [ChunkDTO.model_validate(chunk) for chunk in chunks]
        return None
    # 根据file_id删除chunks
    async def delete_chunks_by_file_id(self,file_id:str):
        await self.dao.delete_chunks_by_file_id(file_id)

    # 批量获取chunks
    async def get_chunks_by_primary_keys(self, chunk_ids: list[str]) -> list[ChunkDTO]:
        if not chunk_ids:
            return []
        chunks = await self.dao.get_chunks_by_primary_keys(chunk_ids)
        if chunks:
            return [ChunkDTO.model_validate(chunk) for chunk in chunks]
        return []

    # 获取未向量化的chunks，一次200条
    async def get_unembedding_chunks(self) -> list[ChunkDTO]:
        chunks = await self.dao.get_unembedding_chunks()
        if chunks:
            return [ChunkEmbeddingDTO.model_validate(chunk) for chunk in chunks]
        return None

    # 批量更新chunk的向量状态
    async def batch_update_status_by_uuids(self, uuids: list[str], new_status: int) -> None:
        await self.dao.batch_update_status_by_uuids(uuids, new_status)