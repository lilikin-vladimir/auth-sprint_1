import logging
from http import HTTPStatus

from ..fixtures.client import AsyncClient


async def search_sort(query: str, status_code: int,
                      result: list | None, async_client: AsyncClient) -> None:
    """
    Проверка запросов на сортировку данных
    :param query: url запрос
    :param status_code: статус выполнения запроса
    :param result: результат выполнения запроса номер [uuid первый,uuid последний]
    :param async_client: @pytest_fixture
    :return:
    """
    response = await async_client.get(query)
    logging.info(f'Тестируем запрос на сортировку {query}')
    logging.info(f'Запрос {query} первый={response.json()[0].get("uuid", None)} последний'
                 f'= {response.json()[-1].get("uuid", None)} \n{response.json()}')

    assert response.status_code == status_code
    if response.status_code == HTTPStatus.OK:
        assert len(response.json()) > 1, "Результатов запроса должно быть более 1"
        assert isinstance(response.json(), list), "Результат запроса должен быть списком"
        assert response.json()[0].get('uuid', None) == result[
            0], f'Неверная сортировка {query}    по первому значению'
        assert response.json()[-1].get('uuid', None) == result[
            1], f'Неверная сортировка {query}   по последнему значению'
