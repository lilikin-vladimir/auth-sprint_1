from functools import lru_cache

from fastapi import Depends

from models.base import FilmInfo
from models.params import FilmsSearch
from models.response_film import FilmFullInfoResponse
from search_engines.base import AsyncSearchEngine
from search_engines.elastic import ElasticAsyncSearchEngine
from services.base import BaseService


class FilmService(BaseService):
    full_schema = FilmFullInfoResponse
    search_result_schema = FilmInfo

    async def search(self, params: FilmsSearch) -> list[FilmInfo]:
        result = await self.search_engine.search_films(params=params)
        return [self.search_result_schema(**item) for item in result]


@lru_cache()
def get_film_service(
        search_engine: AsyncSearchEngine = Depends(ElasticAsyncSearchEngine.get_engine(index='movies')),
) -> FilmService:
    return FilmService(search_engine)
