import uuid
from pgvector.utils import Vector
from src.db.pg_db import get_db
from src.services.chunk_service import ChunkService
from src.handler.embedding.embedding_model_handler import get_embedding_model
import asyncio
from src.dto.embedding_dto import EmbeddingDTO
from src.services.embedding_service import EmbeddingService
from datetime import datetime
from src.utils.logger import get_logger
logger = get_logger(__name__)



# 获取未向量化的chunks
async def get_unembedding_chunks():
    async for session in get_db():
        service = ChunkService(session)
        unembedding_chunks = await service.get_unembedding_chunks()
    return unembedding_chunks


# 向量化
async def embedding_chunks(chunks):
    embedding_model = await get_embedding_model()
    texts = [chunk.context for chunk in chunks]
    chunks_id = [chunk.chunk_id for chunk in chunks]
    embeddings = embedding_model.embed_documents(texts)
    embedding_dict = dict(zip(tuple(chunks_id),embeddings))
    return embedding_dict


# 存入数据库
async def batch_create_embeddings():
    embedding_dto_list = []
    unembedding_chunks = await get_unembedding_chunks()
    if unembedding_chunks:
        embedding_dict = await embedding_chunks(unembedding_chunks)
        for unembedding_chunk in unembedding_chunks:
            embedding_dto_list.append(
                EmbeddingDTO(
                    uuid=uuid.uuid4(),
                    space_id=unembedding_chunk.space_id,
                    file_id=unembedding_chunk.file_id,
                    chunk_id=unembedding_chunk.chunk_id,
                    embedding_vector=Vector(embedding_dict[unembedding_chunk.chunk_id]),
                    search_vector=unembedding_chunk.context,
                    create_time=datetime.now()
                )
            )
        async for session in get_db():
            embedding_service = EmbeddingService(session)
            await embedding_service.batch_create_embeddings(embedding_dto_list)
            chunk_service = ChunkService(session)
            await chunk_service.batch_update_status_by_uuids([chunk.chunk_id for chunk in unembedding_chunks],1)


async def schedul_job():
    try:
        while True:
            logger.info("正在以30s每轮循环执行向量化任务。。。")
            await batch_create_embeddings()
            await asyncio.sleep(30)
    except asyncio.CancelledError:
        logger.info("循环执行向量化任务已取消。。。")
        raise



