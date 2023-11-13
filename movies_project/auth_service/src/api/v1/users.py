from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter
from fastapi_pagination import Page

from schemas.roles import RoleInDB, AddRole
from schemas.users import UserResponseData, UserForUpdate, UserHistory
from services.auth import TokenDep, get_user_id_from_token
from services.database import DbDep
from services.exceptions import wrong_username_or_password_exception, permission_denied
from services.users import (
    get_paginated_history, update_user_credentials, get_role, add_role, remove_role
)


router = APIRouter()


@router.put(
    "/update-credentials/",
    summary="Обновить email и/или пароль пользователя",
    response_model=UserResponseData,
    description="Обновить email и/или пароль пользователя",
    status_code=HTTPStatus.OK
)
async def update_credentials(user: UserForUpdate, db: DbDep) -> UserResponseData:
    updated_user = await update_user_credentials(user, db)

    if not updated_user:
        raise wrong_username_or_password_exception

    return updated_user


@router.get(
    "/{user_id}/auth-history/",
    summary="История входов пользователя",
    response_model=Page[UserHistory],
    description="Получить историю входов пользователя",
    status_code=HTTPStatus.OK
)
async def get_auth_history(user_id: UUID, token: TokenDep, db: DbDep) -> list[UserHistory]:
    if await get_user_id_from_token(token) != user_id:
        raise permission_denied

    return await get_paginated_history(user_id, db)


@router.get(
    "/{user_id}/roles/",
    summary="Роль пользователя",
    response_model=RoleInDB | None,
    description="Получить текущую роль пользователя",
    status_code=HTTPStatus.OK
)
async def get_user_roles(user_id: UUID, token: TokenDep, db: DbDep) -> RoleInDB | None:
    if await get_user_id_from_token(token) != user_id:
        raise permission_denied

    return await get_role(user_id, db)


@router.post(
    "/{user_id}/roles/",
    summary="Установить роль пользователю",
    description="Установить роль пользователю",
    status_code=HTTPStatus.NO_CONTENT
)
async def add_user_role(user_id: UUID, role: AddRole, token: TokenDep, db: DbDep):
    if await get_user_id_from_token(token) != user_id:
        raise permission_denied

    return await add_role(user_id, role.role_id, db)


@router.delete(
    "/{user_id}/roles/",
    summary="Удалить роль пользователя",
    description="Удалить роль пользователя",
    status_code=HTTPStatus.NO_CONTENT
)
async def remove_user_role(user_id: UUID, token: TokenDep, db: DbDep):
    if await get_user_id_from_token(token) != user_id:
        raise permission_denied

    return await remove_role(user_id, db)
