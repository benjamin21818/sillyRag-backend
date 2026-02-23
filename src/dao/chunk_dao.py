from src.dao.base_dao import BaseDao
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.models.chunk import Chunk
from src.models.files import File
from sqlalchemy import select, delete, update
from sqlalchemy.orm import joinedload


class ChunkDao(BaseDao):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Chunk)


    # 根据file_id获取chunks
    async def get_by_file_id(self, file_id: UUID):
        result = await self.session.execute(
            select(Chunk)
            .options(joinedload(Chunk.file))
            .where(Chunk.file_id == file_id)
        )
        return result.scalars().all()


    # 获取多个chunks，base里的是获取单个
    async def get_chunks_by_primary_keys(self, chunk_ids: list[UUID]):
        stmt = select(Chunk).where(Chunk.uuid.in_(chunk_ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()


    # 根据file_id删除chunks
    async def delete_chunks_by_file_id(self, file_id: UUID):
        await self.session.execute(delete(Chunk).where(Chunk.file_id == file_id))
        await self.session.commit()


    
    async def get_unembedding_chunks(self):
        stmt = (
            select(
                Chunk.uuid.label("chunk_id"),
                File.space_id,
                Chunk.file_id,
                Chunk.file_name,
                Chunk.context
            )
            .join(File, Chunk.file_id == File.uuid)
            .where(Chunk.status == 0)
            .order_by(Chunk.create_time.asc())
            .limit(200)
        )
        result = await self.session.execute(stmt)
        return result.mappings().all()



    # 批量更新chunk状态
    async def batch_update_status_by_uuids(self, uuids: list[UUID], new_status: int):
        stmt = (
            update(Chunk)
            .where(Chunk.uuid.in_(uuids))
            .values(status=new_status)
            .returning(Chunk.uuid)  # 返回受影响的 UUID 列表
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalars().all()
