from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter
from fastapi_pagination import Page

from schemas.roles import RoleInDB, AddRole
from schemas.users import (
    UserResponseData, UserForUpdate,
    UserHistory,
)
from services.auth import AuthServiceDep
from services.users import UserServiceDep
from services.exceptions import (
    wrong_username_or_password_exception,
    permission_denied,
)

router = APIRouter()


@router.put(
    "/update-credentials/",
    summary="Обновить email и/или пароль пользователя",
    response_model=UserResponseData,
    description="Обновить email и/или пароль пользователя",
    status_code=HTTPStatus.OK
)
async def update_credentials(user: UserForUpdate,
                             user_service: UserServiceDep
                             ) -> UserResponseData:
    updated_user = await user_service.update_user_credentials(user)

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
async def get_auth_history(user_id: UUID, token: str,
                           user_service: UserServiceDep,
                           auth_service: AuthServiceDep
                           ) -> list[UserHistory]:
    token = await auth_service.check_access_token(token)
    if await auth_service.get_user_id_from_token(token) != user_id:
        raise permission_denied

    history_list = await user_service.get_paginated_history(user_id)
    return history_list


@router.get(
    "/{user_id}/roles/",
    summary="Роль пользователя",
    response_model=RoleInDB | None,
    description="Получить текущую роль пользователя",
    status_code=HTTPStatus.OK
)
async def get_user_roles(user_id: UUID, token: str,
                         user_service: UserServiceDep,
                         auth_service: AuthServiceDep
                         ) -> RoleInDB | None:
    token = await auth_service.check_access_token(token)
    if await auth_service.get_user_id_from_token(token) != user_id:
        raise permission_denied

    role = await user_service.get_role(user_id)
    return role


@router.post(
    "/{user_id}/roles/",
    summary="Установить роль пользователю",
    description="Установить роль пользователю",
    status_code=HTTPStatus.NO_CONTENT
)
async def add_user_role(user_id: UUID, role: AddRole, token: str,
                        user_service: UserServiceDep,
                        auth_service: AuthServiceDep) -> None:
    token = await auth_service.check_access_token(token)
    if await auth_service.get_user_id_from_token(token) != user_id:
        raise permission_denied

    await user_service.add_role(user_id, role.role_id)


@router.delete(
    "/{user_id}/roles/",
    summary="Удалить роль пользователя",
    description="Удалить роль пользователя",
    status_code=HTTPStatus.NO_CONTENT
)
async def remove_user_role(user_id: UUID, token: str,
                           user_service: UserServiceDep,
                           auth_service: AuthServiceDep) -> None:
    token = await auth_service.check_access_token(token)
    if await auth_service.get_user_id_from_token(token) != user_id:
        raise permission_denied

    await user_service.remove_role(user_id)
