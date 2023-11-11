import pytest
import asyncio


pytest_plugins = (
    "tests.functional.fixtures.pg_fixtures",
    "tests.functional.fixtures.aiohttp_fixtures",
)


@pytest.fixture(scope='session')
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
