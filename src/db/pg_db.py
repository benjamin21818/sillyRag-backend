import urllib
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import urllib.parse
import psycopg
import os
from src.utils.conf import BASE_DIR
from dotenv import load_dotenv

load_dotenv(os.path.join(BASE_DIR, ".env"))


def get_db_url():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

# 管理数据库连接池
engine = create_async_engine(
    get_db_url(),
    pool_size=10,
    pool_recycle=3600,
    max_overflow=20,
    pool_pre_ping=True
)
# 从连接池中获取会话
async_session = sessionmaker(
    engine,
    class_=AsyncSession,# 指定生成的 Session 类型为异步 Session
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        db = async_session()
        yield db
    except Exception as e:
        print(e)
        if db and db.in_transaction():
            await db.rollback()
        raise e
    finally:
        await db.close()


async def create_async_connection():
    parsed = urllib.parse.urlparse(get_db_url())
    conn_str = f"user={parsed.username} password={parsed.password} host={parsed.hostname} port={parsed.port} dbname={parsed.path.lstrip('/')}"
    return await psycopg.AsyncConnection.connect(conn_str)