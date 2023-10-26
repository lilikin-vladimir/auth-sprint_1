from http import HTTPStatus

import pytest

from ..fixtures.client import AsyncClient
from ..test_func.test_func_paginator import search_paginator
from ..test_func.test_func_query import search_query
from ..test_func.test_func_sort import search_sort


@pytest.mark.parametrize("query, status_code, result,",
                         # ----Тестирование FILMS-------------------------------------------------
                         [("/films/search?query=Star&page_number=1&page_size=2",
                           HTTPStatus.OK, [{
                             "uuid": "00af52ec-9345-4d66-adbe-50eb917f463a",
                             "title": "Star Slammer",
                             "imdb_rating": 3.5}, {
                             "uuid": "00e2e781-7af9-4f82-b4e9-14a488a3e184",
                             "title": "Star Wars: X-Wing",
                             "imdb_rating": 8.1}]),

                          ("/films/search?query=Иван&page_number=1&page_size=2",
                           HTTPStatus.NOT_FOUND, []),

                          ("/films/search?genre=3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff&page_number=1&page_size=2",
                           HTTPStatus.OK, [{
                              "uuid": "00af52ec-9345-4d66-adbe-50eb917f463a",
                              "title": "Star Slammer",
                              "imdb_rating": 3.5}, {
                              "uuid": "00e2e781-7af9-4f82-b4e9-14a488a3e184",
                              "title": "Star Wars: X-Wing",
                              "imdb_rating": 8.1}]),

                          ("/films/search?person=a5a8f573-3cee-4ccc-8a2b-91cb9f55250a&page_number=1&page_size=2",
                           HTTPStatus.OK, [{
                              "uuid": "025c58cd-1b7e-43be-9ffb-8571a613579b",
                              "title": "Star Wars: Episode VI - Return of the Jedi",
                              "imdb_rating": 8.3}, {
                              "uuid": "0312ed51-8833-413f-bff5-0e139c11264a",
                              "title": "Star Wars: Episode V - The Empire Strikes Back",
                              "imdb_rating": 8.7}]),

                          ("/films/0312ed51-8833-413f-bff5-0e139c11264a",
                           HTTPStatus.OK, {
                               "actors": [{"full_name": "Mark Hamill", "uuid": "26e83050-29ef-4163-a99d-b546cac208f8"},
                                          {"full_name": "Harrison Ford",
                                           "uuid": "5b4bf1bc-3397-4e83-9b17-8b10c6544ed1"},
                                          {"full_name": "Carrie Fisher",
                                           "uuid": "b5d2b63a-ed1f-4e46-8320-cf52a32be358"},
                                          {"full_name": "Billy Dee Williams",
                                           "uuid": "efdd1787-8871-4aa9-b1d7-f68e55b913ed"}],
                               "description": "Luke Skywalker, Han Solo, Princess Leia and "
                                              "Chewbacca face attack by the Imperial forces and "
                                              "its AT-AT walkers on the ice planet Hoth. While "
                                              "Han and Leia escape in the Millennium Falcon, "
                                              "Luke travels to Dagobah in search of Yoda. Only "
                                              "with the Jedi master's help will Luke survive "
                                              "when the dark side of the Force beckons him into "
                                              "the ultimate duel with Darth Vader.",
                               "directors": [
                                   {"full_name": "Irvin Kershner", "uuid": "1989ed1e-0c0b-4872-9dfb-f5ed13c764e2"}],
                               "genres": [{"uuid": "120a21cf-9097-479e-904a-13dd7198c1dd", "name": "Adventure"},
                                          {"uuid": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", "name": "Action"},
                                          {"uuid": "6c162475-c7ed-4461-9184-001ef3d9f26e", "name": "Sci-Fi"},
                                          {"uuid": "b92ef010-5e4c-4fd0-99d6-41b6456272cd", "name": "Fantasy"}],
                               "uuid": "0312ed51-8833-413f-bff5-0e139c11264a",
                               "imdb_rating": 8.7,
                               "title": "Star Wars: Episode V - The Empire Strikes Back",
                               "writers": [
                                   {"full_name": "Lawrence Kasdan", "uuid": "3217bc91-bcfc-44eb-a609-82d228115c50"},
                                   {"full_name": "George Lucas", "uuid": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a"},
                                   {"full_name": "Leigh Brackett", "uuid": "ed149438-4d76-45c9-861b-d3ed48ccbf0c"}],
                           }), ])
async def test_search_query(query: str, status_code: int, result: list | dict,
                            async_client: AsyncClient):
    """
    Тестирование поиска
    :param query: тестируемый URL запрос
    :param status_code: статус код выполненного URL запроса
    :param result: результат выполнения запроса эталонный
    :param async_client: @pytest_fixture aiohttp
    :return:
    """
    await search_query(query, status_code, result, async_client)


@pytest.mark.parametrize("query,index_paginator, status_code,  result", [
    ('/films/search?query=Star', [1, 2], HTTPStatus.OK, 2),
    ('/films/search?query=Star', [1, 50], HTTPStatus.OK, 50),
    ('/films/search?person=a5a8f573-3cee-4ccc-8a2b-91cb9f55250a', [1, 2], HTTPStatus.OK, 2),
    ('/films/search?person=a5a8f573-3cee-4ccc-8a2b-91cb9f55250a', [1, 50], HTTPStatus.OK, 46)])
async def test_paginator_query(query: str, index_paginator: list,
                               status_code: int, result: int, async_client: AsyncClient):
    """
    Тестирование поиска
    :param query: тестируемый URL запрос
    :param index_paginator:
    :param status_code: статус код выполненного URL запроса
    :param result: количество данных в результате запроса
    :param async_client: @pytest_fixture aiohttp
    :return:
    """
    await search_paginator(query, index_paginator, status_code, result, async_client)


@pytest.mark.parametrize("query, status_code, result,", [
    ('/films/search?query=Star&sort=imdb_rating', HTTPStatus.OK,
     ["e7e6d147-cc10-406c-a7a2-5e0be2231327", "5c855467-9c2b-491d-a179-c217ea543e93"]),
    ('/films/search?query=Star&sort=-imdb_rating', HTTPStatus.OK,
     ["2a090dde-f688-46fe-a9f4-b781a985275e", "833b1926-ef16-49a1-b41d-eddd618a036e"]),

    ('/films/search?query=Star&sort=imdb_rating', HTTPStatus.OK,
     ["e7e6d147-cc10-406c-a7a2-5e0be2231327", "5c855467-9c2b-491d-a179-c217ea543e93"]),
    ('/films/search?query=Star&sort=-imdb_rating', HTTPStatus.OK,
     ["2a090dde-f688-46fe-a9f4-b781a985275e", "833b1926-ef16-49a1-b41d-eddd618a036e"]),

    ('/films/search?person=a5a8f573-3cee-4ccc-8a2b-91cb9f55250a&sort=imdb_rating', HTTPStatus.OK,
     ["134989c3-3b20-4ae7-8092-3e8ad2333d59", "6cb927b3-4760-46c8-9002-ff4a47d57a4a"]),
    ('/films/search?person=a5a8f573-3cee-4ccc-8a2b-91cb9f55250a&sort=-imdb_rating', HTTPStatus.OK,
     ["e5a21648-59b1-4672-ac3b-867bcd64b6ea", "3cb639db-cd8a-48b0-90e3-9def109a4492"]),

    ('/films?genre=526769d7-df18-4661-9aa6-49ed24e9dfd8&sort=imdb_rating', HTTPStatus.OK,
     ["c97c8fbc-4084-4e9b-a486-eb5fcfe6104b", "b9514b7a-eab8-4f4e-aebc-157d4e3a1719"]),
    ('/films?genre=526769d7-df18-4661-9aa6-49ed24e9dfd8&sort=-imdb_rating', HTTPStatus.OK,
     ["ea434935-cb62-4012-9138-be74435890cd", "98167b6e-8d41-4378-9fc3-ee998677e6cb"])])
async def test_sort_query(query: str, status_code: int,
                          result: list[str, str], async_client: AsyncClient):
    """
    Тестирование поиска
    :param query: тестируемый URL запрос
    :param status_code: статус код выполненного URL запроса
    :param result: результат выполнения запроса номер [uuid первый,uuid последний]
    :param async_client: @pytest_fixture aiohttp
    :return:
    """
    await search_sort(query, status_code, result, async_client)
