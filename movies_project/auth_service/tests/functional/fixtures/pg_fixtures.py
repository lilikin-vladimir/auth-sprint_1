import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession, AsyncEngine, AsyncConnection
)

from tests.functional.settings import settings
from tests.functional.testdata.pg_models import Base


@pytest_asyncio.fixture(scope='session')
async def async_engine() -> AsyncEngine:
    return create_async_engine(
        f'postgresql+asyncpg://'
        f'{settings.pg_user}:{settings.pg_pass}@'
        f'{settings.pg_host}:{settings.pg_port}/'
        f'{settings.pg_db}',
        future=True
    )


@pytest_asyncio.fixture(scope='session')
async def async_connection(async_engine: AsyncEngine) -> AsyncConnection:
    async with async_engine.connect() as connection:
        yield connection


@pytest_asyncio.fixture(scope='function')
async def async_session(async_connection: AsyncConnection):
    async with AsyncSession(bind=async_connection) as session:
        yield session


@pytest.fixture(scope='function')
def pg_add_instances(async_session: AsyncSession):
    async def inner(instances: list):
        try:
            async_session.add_all(instances)
            await async_session.commit()
        except Exception as err:
            raise Exception(f'Ошибка записи данных в Postgres: {err}')

    return inner


async def clear_db_tables(async_session: AsyncSession):
    for table in reversed(Base.metadata.sorted_tables):
        await async_session.execute(table.delete())
    await async_session.commit()


@pytest_asyncio.fixture(scope='function', autouse=True)
async def cleanup_db(async_session: AsyncSession):
    yield
    await clear_db_tables(async_session)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def prepare_db(async_connection: AsyncConnection):
    async with AsyncSession(bind=async_connection) as session:
        await clear_db_tables(session)
