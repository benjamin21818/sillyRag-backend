import asyncio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.handler.embedding.embedding_model_handler import init_embedding_model
from src.handler.embedding.embedding_chunks_handler import schedul_job
from src.handler.partition.partition_handler import schedul_partition_job
from src.api import router as router
from fastapi.middleware.cors import CORSMiddleware
from src.utils.logger import get_logger
from src.utils.conf import BASE_DIR
import os
logger = get_logger(__name__)


async def lifespan(app:FastAPI):
    try:
        await init_embedding_model()
        logger.info("初始化向量模型成功。。。")
    except Exception as e:
        raise
    task = asyncio.create_task(schedul_job())
    logger.info("定时向量化任务启动成功。。。")
    partition_task = asyncio.create_task(schedul_partition_job())
    logger.info("定时分块任务启动成功。。。")
    try:
        yield # 表示应用进入正常运行状态
    finally:
        task.cancel()
        partition_task.cancel()
        try:
            await task
            await partition_task
        except asyncio.CancelledError:
            logger.info("定时向量化任务取消成功。。。")
            logger.info("定时分块任务取消成功。。。")



app = FastAPI(lifespan=lifespan)

# 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 挂载静态文件目录，用于访问生成的音频文件
uploads_dir = os.path.join(BASE_DIR, "uploads")

asr_voice_dir = os.path.join(uploads_dir, "asr_voice")
if not os.path.exists(asr_voice_dir):
    os.makedirs(asr_voice_dir)
app.mount("/uploads/asr_voice", StaticFiles(directory=asr_voice_dir), name="uploads_asr_voice")

tts_voice_dir = os.path.join(uploads_dir, "tts_voice")
if not os.path.exists(tts_voice_dir):
    os.makedirs(tts_voice_dir)
app.mount("/uploads/tts_voice", StaticFiles(directory=tts_voice_dir), name="uploads_tts_voice")



app.include_router(router)
