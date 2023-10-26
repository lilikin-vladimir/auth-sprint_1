from typing import Annotated
from uuid import UUID

from fastapi import Query


class BasePaginator:
    def __init__(
            self,
            page_number: Annotated[int, Query(description='Номер страницы', ge=1, le=1000)] = 1,
            page_size: Annotated[int, Query(description='Размер страницы', ge=1, le=50)] = 10,
            sort: Annotated[str, Query(description='Сортировка по убыванию -id по возрастанию id')] = 'id'
    ) -> None:
        self.page_number = page_number
        self.page_size = page_size
        self.sort = sort

    def paginator(self) -> dict:
        return {'page_number': self.page_number,
                'page_size': self.page_size, 'sort': self.sort}

    def __repr__(self):
        return f'BasePaginator(page_number={self.page_number}, page_size={self.page_size}, sort={self.sort})'


class BaseIdParams:
    def __init__(self, id_uuid: UUID) -> None:
        self.id_str = str(id_uuid)

    def __repr__(self):
        return f'BaseIdParams(id_uuid={self.id_str})'
