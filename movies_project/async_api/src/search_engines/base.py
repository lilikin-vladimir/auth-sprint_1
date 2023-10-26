from abc import ABC, abstractmethod
from typing import Callable

from models.params import BaseList, FilmsSearch, PersonsSearch


class AsyncSearchEngine(ABC):

    @staticmethod
    @abstractmethod
    def get_engine(**kwargs) -> Callable:
        """Метод должен возвращать функцию для создания экземпляра класса AsyncSearchEngine.
        Принятые kwargs могут быть переданы в конструктор класса при вызове возвращаемой функции.
        """
        pass

    @abstractmethod
    async def get_by_id(self, _id: str) -> dict | None:
        pass

    @abstractmethod
    async def get_list(self, params: BaseList) -> list[dict]:
        pass

    @abstractmethod
    async def search_films(self, params: FilmsSearch) -> list[dict]:
        """Метод для поиска фильмов. Формирует тело запроса и выполняет обычный поиск"""

    @abstractmethod
    async def search_persons(self, params: PersonsSearch) -> list[dict]:
        pass
