from src.dao.base_dao import BaseDao
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, text
from src.models.embedding import Embedding
import json
from uuid import UUID
from src.handler.jieba_tool import clean_text
from src.utils.serializers import json_serializer


class EmbeddingDao(BaseDao):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Embedding)


    # 根据文件id删除向量
    async def delete_embeddings_by_file_id(self, file_id: UUID):
        await self.session.execute(delete(self.model).where(self.model.file_id == file_id))
        await self.session.commit()


    async def batch_create_embeddings(self, items: list):
        """
        批量插入 Embedding 数据，并在插入时计算 search_vector 字段为 to_tsvector('jiebacfg',search_vector)
        :param items: 包含多个模型对象的列表
        """
        data = [
            {
                "uuid": item.uuid,
                "space_id": item.space_id,
                "file_id": item.file_id,
                "chunk_id": item.chunk_id,
                "embedding_vector": item.embedding_vector.to_list(),
                "search_vector": clean_text(item.search_vector),
                "create_time": item.create_time,   
            }
            for item in items
        ]

        insert_sql = text(
            """
            INSERT INTO embedding (uuid, space_id, file_id, chunk_id, embedding_vector, search_vector, create_time)
            SELECT 
                (element->>'uuid')::UUID,
                (element->>'space_id')::UUID,  
                (element->>'file_id')::UUID,
                (element->>'chunk_id')::UUID,
                (element->>'embedding_vector')::VECTOR,
                to_tsvector('jiebacfg',element->>'search_vector'), 
                (element->>'create_time')::TIMESTAMP WITH TIME ZONE
            FROM json_array_elements(:data) AS element
            """
        )

        await self.session.execute(insert_sql, {"data": json.dumps(data,default = json_serializer)})
        await self.session.commit()
