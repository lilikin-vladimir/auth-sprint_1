import logging
from http import HTTPStatus

from ..fixtures.client import AsyncClient


async def search_query(query: str, status_code: int,
                       result: list | dict, async_client: AsyncClient) -> None:
    """
    Проверка запросов на вводимые параметры
    :param query: url запрос
    :param status_code: статус выполнения запроса
    :param result: результат выполнения запроса эталонный
    :param async_client: @pytest_fixture
    :return:
    """

    response = await async_client.get(query)
    logging.info(f'Тестируем запрос параметры -> результат {query}')
    assert response.status_code == status_code

    if response.status_code == HTTPStatus.OK:
        assert response.json() == result
