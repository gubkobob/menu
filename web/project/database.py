import redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import REDIS_HOST, REDIS_PORT, settings

engine = create_async_engine(settings.url, echo=settings.echo)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
session = async_session()
Base = declarative_base()


async def get_session():
    async with async_session() as session:
        yield session

redis_client = redis.Redis(host=f'{REDIS_HOST}', port=int(f'{REDIS_PORT}'), encoding='utf8')
