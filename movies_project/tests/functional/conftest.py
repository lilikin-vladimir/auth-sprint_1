import asyncio

from pytest import FixtureRequest
from redis.asyncio import Redis

from .fixtures.client import *


@pytest_asyncio.fixture(scope='session')
def event_loop(request: FixtureRequest) -> None:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def redis_client() -> Redis:
    client = Redis(host=config.redis_host, port=config.redis_port)
    yield client
