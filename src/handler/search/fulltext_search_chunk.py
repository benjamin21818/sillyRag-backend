
from sqlalchemy import text
from src.db.pg_db import get_db
from src.handler.jieba_tool import to_query
import asyncio

class FulltextSearchChunk:
    def __init__(self):
        pass


    async def fulltext_search_chunk(self,message:str,top_n:int,threshold_fulltext:float,space_id:str = None):

        # 1. 使用 jieba 对搜索词进行分词处理
        query_str = to_query(message)
        if not query_str or query_str.strip() == "":
            return []
        
        # 修复 tsquery 语法错误：移除分词结果中多余的 | 和空白符
        # 比如 "有氧 | 运动 |   | 跑步" -> "有氧 | 运动 | 跑步"
        query_parts = [p.strip() for p in query_str.split('|') if p.strip()]
        query_str = " | ".join(query_parts)
        
        if not query_str:
            return []


        # 2. 定义全文检索 SQL
        # 使用 ts_rank 计算相关度得分
        sql = """
            SELECT chunk_id
            FROM (
                SELECT 
                    chunk_id,
                    ts_rank(search_vector, to_tsquery('jiebacfg', :query), 32) AS similarity
                FROM embedding 
                WHERE space_id = :space_id
                  AND to_tsquery('jiebacfg', :query) @@ search_vector
            ) sub
            WHERE similarity > :threshold
            ORDER BY similarity DESC
            LIMIT :top_n
        """

        # 3. 执行查询
        async for session in get_db():
            result = await session.execute(
                text(sql),
                {
                    "query": query_str,
                    "space_id": space_id,
                    "threshold": threshold_fulltext,
                    "top_n": top_n
                }
            )
            # 获取所有匹配的 chunk_id
            chunk_ids = [row[0] for row in result.fetchall()]
        return chunk_ids



# if __name__ == '__main__':
#     fulltext_search_chunk = FulltextSearchChunk()
#     result = asyncio.run(fulltext_search_chunk.fulltext_search_chunk("有氧运动（如跑步、游泳）和力量训练", 3, 0,"b39c6ce4-cf60-4d0e-bbc1-13c300e8b884"))
#     print(result)
