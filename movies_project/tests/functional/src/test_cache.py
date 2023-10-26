import json
import logging
from http import HTTPStatus

import pytest
from redis.asyncio import Redis

from ..fixtures.client import AsyncClient


@pytest.mark.parametrize("query, status, substitution", [
    ('/films/search?query=Star', True,
     [{"uuid": "00000000-0000-0000-0000-000000000000",
       "title": "XXXX",
       "imdb_rating": 0}]),

    ('/films/0312ed51-8833-413f-bff5-0e139c11264a', True,
     {"uuid": "string",
      "title": "string",
      "imdb_rating": 0,
      "description": "string",
      "genres": [{"uuid": "string", "name": "string"}],
      "actors": [{"uuid": "string", "full_name": "string"}],
      "writers": [{"uuid": "string", "full_name": "string"}],
      "directors": [{"uuid": "string", "full_name": "string"}]}),

    ('/films?genre=3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff', True,
     [{"uuid": "00af52ec-9345-4d66-adbe-50eb917f463a",
       "title": "Star Slammer",
       "imdb_rating": 3.5}]),

    ('/genres/5373d043-3f41-4ea8-9947-4b746c601bbd', True,
     {"uuid": "string",
      "name": "string"}),

    ('/genres', True, [{"name": "Adventure", "uuid": "120a21cf-9097-479e-904a-13dd7198c1dd"}]),

    ('/persons/69b02c62-a329-414d-83c6-ca54be34de24/film', True,
     [{"uuid": "00000000-0000-0000-0000-000000000000",
       "title": "XXXX",
       "imdb_rating": 0}]),

    ('/persons/2d6f6284-13ce-4d25-9453-c4335432c116', True,
     {"uuid": "2d6f6284-13ce-4d25-9453-c4335432c116",
      "full_name": "Adam Driver",
      "films": [{
          "uuid": "12a8279d-d851-4eb9-9d64-d690455277cc", "roles": ["actor"]},
          {"uuid": "1d42ceae-9397-475c-9517-e94dda7bc2a1", "roles": ["actor"]},
          {"uuid": "46f15353-2add-415d-9782-fa9c5b8083d5", "roles": ["actor"]},
          {"uuid": "91f02795-7628-4ef4-acf2-d93b892365dd", "roles": ["actor"]},
          {"uuid": "cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394", "roles": ["actor"]}]}),

    ('/persons/search?query=Woody', True,
     [{"films": [{"roles": ["actor"], "uuid": "57beb3fd-b1c9-4f8a-9c06-2da13f95251c"}],
       "full_name": "Woody Harrelson", "uuid": "01377f6d-9767-48ce-9e37-3c81f8a3c739"},
      ])])
async def test_cache_api(query: str, status: int, substitution: list,
                         async_client: AsyncClient, redis_client: Redis) -> None:
    """
    Проверка запросов на вводимые параметры
    :param query: url запрос
    :param status: есть кэширование url запроса True/False
    :param substitution: значение подмены
    :param async_client: @pytest_fixture aiohttp
    :param redis_client: @pytest_fixture для cache Redis
    :return:
    """
    # Очистка БД REDIS и выполнение запроса
    await redis_client.flushdb()
    response = await async_client.get(query)
    logging.info(f'Тестируем запрос параметры -> результат {query}')

    # Получаем словарь ключей в БД REDIS
    assert response.status_code == HTTPStatus.OK
    redis_keys = await redis_client.keys('*')
    logging.info(f'key ={redis_keys[0]}')

    # Проверяем что в БД REDIS значение единственного ключа соответствует результату запроса
    assert len(redis_keys) == 1
    result = await redis_client.get(redis_keys[0])
    assert json.loads(result) == response.json()

    # Подмена кеша для анализа, что именно он используется
    await redis_client.set(redis_keys[0], json.dumps(substitution))
    result = await redis_client.get(redis_keys[0])
    logging.info(f'После подмены результата кеша {result}')

    # проверка, что подмена значения запроса произошла успешно
    response = await async_client.get(query)
    assert response.json() == substitution
    await redis_client.flushdb()  # очистка кеша
