from abc import ABC
from typing import Any

from models.params import BaseList
from search_engines.base import AsyncSearchEngine


class BaseService(ABC):
    search_result_schema: Any
    full_schema: Any

    def __init__(self, search_engine: AsyncSearchEngine):
        self.search_engine = search_engine

    async def get(self, _id: str) -> Any:
        result = await self.search_engine.get_by_id(_id=_id)
        return self.full_schema(**result) if result else None

    async def get_list(self, params: BaseList) -> list[Any]:
        result = await self.search_engine.get_list(params=params)
        return [self.search_result_schema(**item) for item in result]
