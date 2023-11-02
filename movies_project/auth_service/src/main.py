import logging
from contextlib import asynccontextmanager
from logging import config as logging_config

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from core import logger
from core.config import config
from db import redis, postgres
from api.v1 import auth, users

logging_config.dictConfig(logger.LOGGING)


async def startup():
    redis.cache = redis.get_session()
    postgres.db_session = postgres.get_async_session()


async def shutdown():
    await redis.cache.close()
    await postgres.db_session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = aioredis.from_url(f'redis://{config.redis_host}:{config.redis_port}')
    FastAPICache.init(RedisBackend(redis.redis), prefix="fastapi-cache", expire=config.cache_expire_time)
    yield
    await redis.redis.close()


logging_config.dictConfig(logger.LOGGING)
app = FastAPI(
    title=config.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
app.include_router(users.router, prefix='/api/v1/users', tags=['users'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=logger.LOGGING,
        log_level=logging.DEBUG,
    )
