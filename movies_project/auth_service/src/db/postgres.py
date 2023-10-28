from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from core.config import config

Base = declarative_base(metadata=MetaData(schema='auth'))

engine = create_async_engine(
    config.postgres_db_dns,
    echo=config.postgres_echo,
    future=True
)

async_session = async_sessionmaker(
    engine, class_=AsyncSession,
    expire_on_commit=False
)


# Функция понадобится при внедрении зависимостей
async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session
