from functools import lru_cache

from fastapi import Depends

from models.response_genre import GenreInfoResponse
from search_engines.base import AsyncSearchEngine
from search_engines.elastic import ElasticAsyncSearchEngine
from services.base import BaseService


class GenreService(BaseService):
    search_result_schema = GenreInfoResponse
    full_schema = GenreInfoResponse


@lru_cache()
def get_genre_service(
        search_engine: AsyncSearchEngine = Depends(ElasticAsyncSearchEngine.get_engine(index='genres')),
) -> GenreService:
    return GenreService(search_engine)
