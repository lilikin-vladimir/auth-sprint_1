import logging
from dataclasses import dataclass
from http import HTTPStatus

from ..fixtures.client import AsyncClient


@dataclass
class Params:
    page_size: int | None | str
    page_number: int | None | str
    status_code: HTTPStatus


async def search_paginator(query: str, index_paginator: list,
                           status_code: int, result: int,
                           async_client: AsyncClient) -> None:
    """
    Проверка запросов и пагинатора на количество ответов
    :param query: url запрос
    :param index_paginator: [page_number, page_size]
    :param status_code: код выполнения запроса
    :param result: количество данных в результате запроса
    :param async_client: @pytest_fixture
    :return:
    """

    query_all = query
    query_all += f'&page_number={index_paginator[0]}' if index_paginator[0] else ''
    query_all += f'&page_size={index_paginator[1]}' if index_paginator[1] else ''
    query_all = query_all.replace('?&', '?')

    logging.info(f'Тестируем запрос на пагинацию {query_all}')
    response = await async_client.get(query_all)

    assert response.status_code == status_code
    assert len(response.json()) == result, \
        f'ошибка пагинации {query} page_size={index_paginator[0]} page_number={index_paginator[1]}'
    logging.info('Проверка на ошибки пагинации')
    params_list = [
        Params(page_size=None, page_number=index_paginator[1], status_code=HTTPStatus.OK),
        Params(page_size=index_paginator[0], page_number=None, status_code=HTTPStatus.OK),
        Params(page_size=None, page_number=None, status_code=HTTPStatus.OK),
        Params(page_size=None, page_number=500000, status_code=HTTPStatus.UNPROCESSABLE_ENTITY),
        Params(page_size=1000, page_number=None, status_code=HTTPStatus.NOT_FOUND),
        Params(page_size=0, page_number=0, status_code=HTTPStatus.OK),
        Params(page_size=1, page_number=0, status_code=HTTPStatus.OK),
        Params(page_size=0, page_number=1, status_code=HTTPStatus.OK),
        Params(page_size=1001, page_number=None, status_code=HTTPStatus.UNPROCESSABLE_ENTITY),
        Params(page_size=None, page_number=-1, status_code=HTTPStatus.UNPROCESSABLE_ENTITY),
        Params(page_size=-1, page_number=None, status_code=HTTPStatus.UNPROCESSABLE_ENTITY),
        Params(page_size='a', page_number=index_paginator[1], status_code=HTTPStatus.UNPROCESSABLE_ENTITY),
        Params(page_size=index_paginator[0], page_number='a', status_code=HTTPStatus.UNPROCESSABLE_ENTITY)
    ]

    for params in params_list:
        query_err = query
        query_err += f'&page_number={params.page_size}' if params.page_size else ''
        query_err += f'&page_size={params.page_number}' if params.page_number else ''
        logging.info(f'Тестируем запрос на пагинацию {query_err}')
        query_err = query_err.replace('?&', '?')

        response = await async_client.get(query_err)
        logging.info(f' Проверка запроса на ошибки {query_err} {params}')
        assert response.status_code == params.status_code, f' Проверка запроса на ошибки {query_err} {params}'
