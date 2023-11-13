import logging
from contextlib import asynccontextmanager
from logging import config as logging_config

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination

from core import logger
from core.config import config
from db import redis, postgres
from api.v1 import auth, users, roles

logging_config.dictConfig(logger.LOGGING)


async def startup():
    redis.cache = redis.get_session()
    postgres.db_session = postgres.get_async_session()


async def shutdown():
    await redis.cache.close()
    await postgres.db_session.close()


@asynccontextmanager
async def lifespan(app_: FastAPI):
    await startup()
    yield
    await shutdown()

app = FastAPI(
    title=config.app_name,
    description='API for users auth',
    version='1.0.0',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
app.include_router(users.router, prefix='/api/v1/users', tags=['users'])
app.include_router(roles.router, prefix='/api/v1/roles', tags=['roles'])

add_pagination(app)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.app_host,
        port=config.app_port,
        log_config=logger.LOGGING,
        log_level=logging.DEBUG,
    )
