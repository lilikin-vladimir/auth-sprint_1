from http import HTTPStatus

import pytest

from ..fixtures.client import AsyncClient
from ..test_func.test_func_paginator import search_paginator
from ..test_func.test_func_query import search_query
from ..test_func.test_func_sort import search_sort


@pytest.mark.parametrize(
    "query, status_code, result,",
    # ----Тестирование PERSON-------------------------------------------------
    [("/persons/69b02c62-a329-414d-83c6-ca54be34de24/film",
      HTTPStatus.OK, [{
        "uuid": "3b914679-1f5e-4cbd-8044-d13d35d5236c",
        "title": "Star Wars: Episode I - The Phantom Menace",
        "imdb_rating": 6.5}, {
        "uuid": "516f91da-bd70-4351-ba6d-25e16b7713b7",
        "title": "Star Wars: Episode III - Revenge of the Sith",
        "imdb_rating": 7.5}, {
        "uuid": "943946ed-4a2b-4c71-8e0b-a58a11bd1323",
        "title": "Star Wars: Evolution of the Lightsaber Duel",
        "imdb_rating": 6.8}, {
        "uuid": "c4c5e3de-c0c9-4091-b242-ceb331004dfd",
        "title": "Star Wars: Episode II - Attack of the Clones",
        "imdb_rating": 6.5}]),

     ("/persons/2d6f6284-13ce-4d25-9453-c4335432c116",
      HTTPStatus.OK, {
          "uuid": "2d6f6284-13ce-4d25-9453-c4335432c116",
          "full_name": "Adam Driver",
          "films": [{"uuid": "12a8279d-d851-4eb9-9d64-d690455277cc", "roles": ["actor"]},
                    {"uuid": "1d42ceae-9397-475c-9517-e94dda7bc2a1", "roles": ["actor"]},
                    {"uuid": "46f15353-2add-415d-9782-fa9c5b8083d5", "roles": ["actor"]},
                    {"uuid": "91f02795-7628-4ef4-acf2-d93b892365dd", "roles": ["actor"]},
                    {"uuid": "cddf9b8f-27f9-4fe9-97cb-9e27d4fe3394", "roles": ["actor"]}]}),

     ("/persons/search?query=Woody&page_number=1&page_size=2",
      HTTPStatus.OK, [
          {"films": [{"roles": ["actor"], "uuid": "57beb3fd-b1c9-4f8a-9c06-2da13f95251c"}],
           "full_name": "Woody Harrelson", "uuid": "01377f6d-9767-48ce-9e37-3c81f8a3c739"},
          {"films": [{"roles": ["actor"], "uuid": "754589c1-e304-4ed8-87bc-1ac897529b97"},
                     {"roles": ["actor"], "uuid": "75475f58-c0ea-4d6d-9f78-bb44d971a21f"}],
           "full_name": "Matthew Wood", "uuid": "05cece18-8d6b-4178-89e4-2af0e1afc902"}]), ])
async def test_search_query(query: str, status_code: int, result: list | dict,
                            async_client: AsyncClient):
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
    ('/persons/69b02c62-a329-414d-83c6-ca54be34de24/film?', [1, 2], HTTPStatus.OK, 2),
    ('/persons/69b02c62-a329-414d-83c6-ca54be34de24/film?', [1, 50], HTTPStatus.OK, 4),
    ('/persons/search?query=Woody', [1, 2], HTTPStatus.OK, 2),
    ('/persons/search?query=Woody', [1, 50], HTTPStatus.OK, 13), ])
async def test_paginator_query(query: str, index_paginator: list, status_code: int,
                               result: int, async_client: AsyncClient):
    """
    Тестирование поиска
    :param query: url запрос
    :param index_paginator: [page_number, page_size]
    :param status_code: код выполнения запроса
    :param result: количество данных в результате запроса
    :param async_client: @pytest_fixture
    """
    await search_paginator(query, index_paginator, status_code, result, async_client)


@pytest.mark.parametrize("query, status_code, result,", [
    ('/persons/69b02c62-a329-414d-83c6-ca54be34de24/film?sort=imdb_rating', HTTPStatus.OK,
     ["3b914679-1f5e-4cbd-8044-d13d35d5236c", "516f91da-bd70-4351-ba6d-25e16b7713b7"]),
    ('/persons/69b02c62-a329-414d-83c6-ca54be34de24/film?sort=-imdb_rating', HTTPStatus.OK,
     ["516f91da-bd70-4351-ba6d-25e16b7713b7", "c4c5e3de-c0c9-4091-b242-ceb331004dfd"]), ])
async def test_sort_query(query: str, status_code: int, result: list[str, str],
                          async_client: AsyncClient):
    """
    Тестирование поиска
    :param query: url запрос
    :param status_code: статус выполнения запроса
    :param result: результат выполнения запроса номер [uuid первый,uuid последний]
    :param async_client: @pytest_fixture
    """
    await search_sort(query, status_code, result, async_client)
