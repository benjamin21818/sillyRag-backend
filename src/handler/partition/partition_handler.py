from src.db.pg_db import get_db
from .txt_partition_handler import PartitionTXT
from .pdf_partition_handler import PartitionPDF
from .docx_partition_handler import PartitionDOCX
from .md_partition_handler import PartitionMD
from .csv_partition_handler import PartitionCSV
from src.dto.chunk_dto import ChunkDTO
import uuid
import asyncio
import traceback
from datetime import datetime
import os
from src.services.chunk_service import ChunkService
from src.services.file_service import FileService
from src.utils.logger import get_logger
logger = get_logger(__name__)



class PartitionHandler:
    def __init__(self):
        pass

    async def file_partition(self, file_id: str, space_id: str,file_name: str, file_path: str, file_extension: str):
        try:
            if file_extension == "txt":
                split_docs = await PartitionTXT().partition_txt(file_path)
            elif file_extension == "pdf":
                split_docs = await PartitionPDF().partition_pdf(file_path)
            elif file_extension == "docx":
                split_docs = await PartitionDOCX().partition_docx(file_path)
            elif file_extension == "md":
                split_docs = await PartitionMD().partition_md(file_path)
            elif file_extension == "csv":
                split_docs = await PartitionCSV().partition_csv(file_path) # 使用了向量相似度划分


            # 将切分后的 Document 对象转换为数据库实体对象 ChunkDto
            if not split_docs:
                return None
            chunks_to_insert = []
            for i, doc in enumerate(split_docs):
                context = doc.page_content if hasattr(doc, "page_content") else doc
                chunks_to_insert.append(
                    ChunkDTO(
                        uuid=uuid.uuid4(),
                        file_id=file_id,
                        file_name=file_name,
                        context=context,
                        index=i,
                        status=0,
                        create_time=datetime.now()
                    )
                )

            # 分批次批量插入数据库 Chunk 表
            batch_size = 1000
            total_chunks = len(chunks_to_insert)
            success_count = 0
            async for session in get_db():
                chunk_service = ChunkService(session)
                file_service = FileService(session)
                for i in range(0, total_chunks, batch_size):
                    batch = chunks_to_insert[i:i+batch_size]
                    batch_num = i // batch_size + 1
                    total_batches = (total_chunks + batch_size - 1) // batch_size
                    try:
                        await chunk_service.create_batch(batch)
                        success_count += len(batch)
                        logger.info(f"已成功插入批次 {batch_num}/{total_batches}，共 {success_count}/{total_chunks} 条记录")
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.error(f"批次 {batch_num}/{total_batches} 插入失败：{e}")
                        traceback.print_exc()
                await file_service.update_by_primary_key(file_id, status=1)
                logger.info(f"文件 {file_name} 分割完成，总共插入 {success_count}/{total_chunks} 个 chunks")

        except Exception as e:
            logger.error(f"读取文件 {file_path} 时发生错误: {e}")
            return None


async def get_unpartitioned_files():
    async for session in get_db():
        service = FileService(session)
        unpartitioned_files = await service.get_files_by_status(0)
    return unpartitioned_files


async def batch_partition_files():
    unpartitioned_files = await get_unpartitioned_files()
    if not unpartitioned_files:
        return
    upload_dir = os.getenv("UPLOAD_DIR", "uploads")
    async for session in get_db():
        file_service = FileService(session)
        for file_item in unpartitioned_files:
            file_path = os.path.join(upload_dir, file_item.file_name)
            if not os.path.exists(file_path):
                logger.error(f"文件不存在，无法分割: {file_path}")
                await file_service.update_by_primary_key(file_item.uuid, status=0)
                continue
            await PartitionHandler().file_partition(
                file_id=file_item.uuid,
                space_id=file_item.space_id,
                file_name=file_item.file_name,
                file_path=file_path,
                file_extension=file_item.file_extension
            )


async def schedul_partition_job():
    try:
        while True:
            logger.info("正在以30s每轮循环执行文件分块任务。。。")
            await batch_partition_files()
            await asyncio.sleep(30)
    except asyncio.CancelledError:
        logger.info("循环执行文件分块任务已取消。。。")
        raise
