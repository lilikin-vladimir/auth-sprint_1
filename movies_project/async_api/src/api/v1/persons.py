from http import HTTPStatus

from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi_cache.decorator import cache

from api.v1.base import BasePaginator, BaseIdParams
from core.config import error_message
from models.base import FilmInfo
from models.params import FilmsSearch, PersonsSearch
from models.response_person import PersonInfoResponse
from services.film import FilmService, get_film_service
from services.person import get_person_service, PersonService

router = APIRouter()


@router.get('/{id_uuid}/film', response_model=list[FilmInfo],
            summary="Фильмы по персоне.",
            description='Получение списка фильмов, в которых участвовала данная персона.',
            response_description="Список фильмов.")
@cache()
# /api/v1/persons/<uuid:UUID>/film
async def persons_film(
        params: BasePaginator = Depends(),
        id_uuid: BaseIdParams = Depends(),
        film_service: FilmService = Depends(get_film_service)
) -> list[FilmInfo]:
    films = await film_service.search(params=FilmsSearch(**params.paginator(), person=id_uuid.id_str))
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_message.no_films_with_person_found)
    return films


@router.get('/search', response_model=list[PersonInfoResponse],
            summary="Поиск по персонам.",
            description='Полнотекстовый поиск персоны по указанному параметру query в запросе.',
            response_description="Список персон.")
@cache()
# /api/v1/persons/search?query=captain&page_number=1&page_size=50
async def person_search(
        params: BasePaginator = Depends(),
        query: str = Query(None, description='Запрос'),
        person_service: PersonService = Depends(get_person_service)
) -> list[PersonInfoResponse]:
    persons = await person_service.search(params=PersonsSearch(**params.paginator(), query=query))
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_message.no_person_found)
    return persons


@router.get('/{id_uuid}', response_model=PersonInfoResponse,
            summary="Информация о персоне.",
            description='Получение информации по персоне по её uuid.',
            response_description='Детальная информация о персоне и список фильмов со списком ролей в них.')
@cache()
# /api/v1/persons/<uuid:UUID>/
async def person_by_id(
        id_uuid: BaseIdParams = Depends(),
        person_service: PersonService = Depends(get_person_service)
) -> PersonInfoResponse:
    person = await person_service.get(id_uuid.id_str)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_message.no_person_found)
    return person
