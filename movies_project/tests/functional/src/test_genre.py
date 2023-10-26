from http import HTTPStatus

import pytest

from ..fixtures.client import AsyncClient
from ..test_func.test_func_paginator import search_paginator
from ..test_func.test_func_query import search_query


@pytest.mark.parametrize(
    "query, status_code, result,",
    # ----Тестирование GANRES-------------------------------------------------
    [("/films?genre=526769d7-df18-4661-9aa6-49ed24e9dfd8&sort=-imdb_rating&page_size=2&page_number=1",
      HTTPStatus.OK, [{
        "imdb_rating": 8.0,
        "title": "Star vs. the Forces of Evil",
        "uuid": "ea434935-cb62-4012-9138-be74435890cd"},
          {"imdb_rating": 7.9,
           "title": "Outlaw Star",
           "uuid": "acaa9ff8-b261-4ff4-b194-a99fd7669542"}]),

     ("/genres/5373d043-3f41-4ea8-9947-4b746c601bbd",
      HTTPStatus.OK, {
          "uuid": "5373d043-3f41-4ea8-9947-4b746c601bbd",
          "name": "Comedy", }),

     ("/genres?page_size=2&page_number=1",
      HTTPStatus.OK,
      [{"name": "Western", "uuid": "0b105f87-e0a5-45dc-8ce7-f8632088f390"},
       {"name": "Adventure", "uuid": "120a21cf-9097-479e-904a-13dd7198c1dd"}]),
     ])
async def test_search_query(query: str, status_code: int,
                            result: list | dict, async_client: AsyncClient):
    """
    Тестирование поиска
    :param query: url запрос
    :param status_code: статус выполнения запроса
    :param result: результат выполнения запроса эталонный
    :param async_client: @pytest_fixture
    :return:
    """
    await search_query(query, status_code, result, async_client)


@pytest.mark.parametrize("query,index_paginator, status_code,  result", [
    ('/genres?', [1, 2], HTTPStatus.OK, 2),
    ('/genres?', [1, 50], HTTPStatus.OK, 26), ])
async def test_paginator_query(
        query: str, index_paginator: list,
        status_code: int, result: int, async_client: AsyncClient):
    """
    Тестирование поиска
    :param query: url запрос
    :param index_paginator: [page_number, page_size]
    :param status_code: код выполнения запроса
    :param result: количество данных в результате запроса
    :param async_client: @pytest_fixture
    """
    await search_paginator(query, index_paginator, status_code, result, async_client)
