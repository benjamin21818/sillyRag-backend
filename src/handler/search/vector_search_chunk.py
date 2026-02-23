from sqlalchemy import text
from src.db.pg_db import get_db
from src.handler.embedding.embedding_model_handler import get_embedding_model
import asyncio

class VectorSearchChunk:
    def __init__(self):
        pass


    async def vector_search_chunk(self,message:str,top_n:int,threshold_vector:float,space_id:str = None):
        if not space_id:
            return []

        embedding_model = await get_embedding_model()
        embedding_message = embedding_model.embed_query(message)

        # 2. 定义 SQL 查询
        # 再次修复：PostgreSQL 在参数绑定附近对 :: 转换非常敏感，统一改用 CAST 语法
        sql = """
            SELECT chunk_id 
            FROM (
                SELECT chunk_id, (embedding_vector <=> CAST(:embedding AS VECTOR)) AS similarity 
                FROM embedding 
                WHERE space_id = CAST(:space_id AS UUID)
            ) sub 
            WHERE similarity <= :threshold 
            ORDER BY similarity ASC 
            LIMIT :top_n
        """

        # 3. 执行查询
        async for session in get_db():
            try:
                result = await session.execute(
                    text(sql), 
                    {
                        "embedding": str(embedding_message), 
                        "space_id": space_id,
                        "threshold": threshold_vector,
                        "top_n": top_n
                    }
                )
                # 获取所有匹配的 chunk_id
                chunk_ids = [row[0] for row in result.fetchall()]
                return chunk_ids
            except Exception as e:
                print(f"向量检索SQL执行错误: {e}")
                return []
        
        return []
        




# if __name__ == '__main__':
#     vector_search_chunk = VectorSearchChunk()
#     result = asyncio.run(vector_search_chunk.vector_search_chunk("有氧运动和力量训练", 3, 0.5,"b39c6ce4-cf60-4d0e-bbc1-13c300e8b884"))
#     print(result)