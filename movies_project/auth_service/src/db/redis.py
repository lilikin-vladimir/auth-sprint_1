from redis.asyncio import Redis as AsyncRedis

from core.config import config

redis_session = AsyncRedis(host=config.redis_host, port=config.redis_port, ssl=False)

cache: AsyncRedis | None = None


# Функция понадобится при внедрении зависимостей
async def get_session() -> AsyncRedis:
    return redis_session
