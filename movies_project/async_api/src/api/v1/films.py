from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi_cache.decorator import cache

from api.v1.base import BasePaginator, BaseIdParams
from core.config import error_message
from models.base import FilmInfo
from models.params import FilmsSearch
from models.response_film import FilmFullInfoResponse
from services.film import get_film_service, FilmService

router = APIRouter()


@router.get('/search', response_model=list[FilmInfo],
            summary="Поиск по фильмам.",
            description='Полнотекстовый поиск фильма по указанному параметру query в запросе '
                        'и по переданным uuid жанра в параметре genre и персоны в параметре person, '
                        'с сортировкой по параметру sort и пагинацией.',
            response_description="Список фильмов.")
@cache()
# /api/v1/films/search?query=star&page_number=1&page_size=50
async def film_search(
        params: BasePaginator = Depends(),
        query: str = Query(None, description="Текст для поиска"),
        genre: UUID | None = Query(None, description='Жанр'),
        person: UUID | None = Query(None, description='Персона'),
        film_service: FilmService = Depends(get_film_service)) -> list[FilmInfo]:
    films = await film_service.search(
        params=FilmsSearch(
            **params.paginator(),
            query=query,
            genre=str(genre) if genre else None,
            person=str(person) if person else None
        )
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_message.no_film_found)
    return films


@router.get('/{id_uuid}', response_model=FilmFullInfoResponse,
            summary="Информация о фильме.",
            description='Детальная информация о фильме и список жанров, актёров, режиссёров и писателей.',
            response_description='Фильм с информацией по всем имеющимися полям.')
@cache()
# /api/v1/films/<uuid:UUID>/
async def film_by_id(
        id_uuid: BaseIdParams = Depends(),
        film_service: FilmService = Depends(get_film_service)
) -> FilmFullInfoResponse:
    film = await film_service.get(id_uuid.id_str)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_message.no_film_found)
    return film


@router.get('', response_model=list[FilmInfo],
            summary="Главная страница фильмов.",
            description='На ней выводятся популярные фильмы, с возможностью фильтрации по жанру.',
            response_description='Список фильмов.')
@cache()
# /api/v1/films?genre=<uuid:UUID>&sort=-imdb_rating&page_size=50&page_number=1
async def film_list(
        params: BasePaginator = Depends(),
        genre: UUID | None = Query(None, description='UUID жанра'),
        film_service: FilmService = Depends(get_film_service)
) -> list[FilmInfo]:
    films = await film_service.search(params=FilmsSearch(**params.paginator(), genre=str(genre) if genre else None))
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_message.no_film_found)
    return films
