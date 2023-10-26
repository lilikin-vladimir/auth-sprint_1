from functools import lru_cache
from typing import Callable

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from models.params import BaseList, FilmsSearch, PersonsSearch
from search_engines.base import AsyncSearchEngine


class ElasticAsyncSearchEngine(AsyncSearchEngine):

    def __init__(self, elastic: AsyncElasticsearch, index: str) -> None:
        self.elastic = elastic
        self.index = index

    @staticmethod
    def get_engine(index: str) -> Callable:
        @lru_cache()
        def create_engine(elastic: AsyncElasticsearch = Depends(get_elastic)) -> 'ElasticAsyncSearchEngine':
            return ElasticAsyncSearchEngine(elastic=elastic, index=index)
        return create_engine

    async def get_by_id(self, _id: str) -> dict | None:
        try:
            response = await self.elastic.get(index=self.index, id=_id)
            return response['_source']
        except NotFoundError:
            return None

    async def _search(self, **kwargs) -> list[dict]:
        try:
            doc = await self.elastic.search(index=self.index, **kwargs)
            return [hit['_source'] for hit in doc["hits"]["hits"]]
        except NotFoundError:
            return []

    async def get_list(self, params: BaseList) -> list[dict]:
        return await self._search(**params.base_search_params)

    async def search_films(self, params: FilmsSearch) -> list[dict]:
        genre_filter = None
        person_filter = None
        query_result = {"match_all": {}}
        if params.genre:
            genre_filter = {
                "nested": {
                    "path": "genres",
                    "query": {
                        "term": {
                            "genres.id": str(params.genre)
                        }}}}
        if params.person:
            person_filter = [{
                "nested": {
                    "path": role,
                    "query": {
                        "term": {
                            f"{role}.id": str(params.person)
                        }}}
            } for role in ('actors', 'writers', 'directors')]

        if params.query or genre_filter or person_filter:
            bool_filter = {}
            if genre_filter or person_filter:
                bool_filter["filter"] = {"bool": {}}
            if genre_filter:
                bool_filter["filter"]["bool"]["must"] = genre_filter
            if person_filter:
                bool_filter["filter"]["bool"]["should"] = person_filter
            if params.query:
                bool_filter["must"] = {
                    "multi_match": {
                        "query": params.query,
                        "fields": ["title", "description"],
                        "fuzziness": "auto", }}
            if not (params.query is None and params.person is None and params.genre is None):
                query_result = {"bool": bool_filter}
        return await self._search(query=query_result, **params.base_search_params)

    async def search_persons(self, params: PersonsSearch) -> list[dict]:
        query = None
        if params.query:
            query = {
                "multi_match": {
                    "query": params.query,
                    "fields": ["full_name"],
                    "fuzziness": "auto",
                }
            }
        return await self._search(query=query, **params.base_search_params)
