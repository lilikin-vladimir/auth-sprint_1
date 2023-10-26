from functools import lru_cache

from fastapi import Depends

from models.params import PersonsSearch
from models.response_person import PersonInfoResponse
from search_engines.base import AsyncSearchEngine
from search_engines.elastic import ElasticAsyncSearchEngine
from services.base import BaseService


class PersonService(BaseService):
    search_result_schema = PersonInfoResponse
    full_schema = PersonInfoResponse

    async def search(self, params: PersonsSearch) -> list[PersonInfoResponse]:
        result = await self.search_engine.search_persons(params=params)
        return [self.search_result_schema(**item) for item in result]


@lru_cache()
def get_person_service(
        search_engine: AsyncSearchEngine = Depends(ElasticAsyncSearchEngine.get_engine(index='persons')),
) -> PersonService:
    return PersonService(search_engine)
