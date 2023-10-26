from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi_cache.decorator import cache

from api.v1.base import BasePaginator, BaseIdParams
from core.config import error_message
from models.params import BaseList
from models.response_genre import GenreInfoResponse
from services.genre import get_genre_service, GenreService

router = APIRouter()


@router.get('/{id_uuid}', response_model=GenreInfoResponse,
            summary="Информация о жанре.",
            response_description='Информация о жанре.')
@cache()
# /api/v1/genres/<uuid:UUID>
async def genre_details(
        id_uuid: BaseIdParams = Depends(),
        genre_service: GenreService = Depends(get_genre_service)
) -> GenreInfoResponse:
    genre = await genre_service.get(id_uuid.id_str)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_message.no_genre_found)
    return genre


@router.get('', response_model=list[GenreInfoResponse],
            summary="Список жанров.",
            response_description='Список жанров.')
@cache()
# /api/v1/genres/
async def genres_details_list(
        params: BasePaginator = Depends(),
        genre_service: GenreService = Depends(get_genre_service)
) -> list[GenreInfoResponse]:
    genres = await genre_service.get_list(params=BaseList(**params.paginator()))
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=error_message.no_genres_found)
    return genres
