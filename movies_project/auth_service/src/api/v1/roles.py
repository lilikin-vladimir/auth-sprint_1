from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter

from schemas.roles import RoleInDB, RoleCreate
from services.auth import AuthServiceDep
from services.roles import RoleServiceDep


router = APIRouter()


@router.get(
    "/",
    summary="Получить роли",
    response_model=list[RoleInDB],
    description="Получить список всех ролей",
    status_code=HTTPStatus.OK
)
async def get_all_roles(
    token: str,
    auth_service: AuthServiceDep,
    role_service: RoleServiceDep
) -> list[RoleInDB]:
    await auth_service.check_access_token(token)
    return await role_service.get_roles()


@router.post(
    "/",
    summary="Создать роль",
    response_model=RoleInDB,
    description="Создать роль",
    status_code=HTTPStatus.CREATED
)
async def create_role(
    role: RoleCreate, token: str,
    auth_service: AuthServiceDep,
    role_service: RoleServiceDep
) -> RoleInDB:
    await auth_service.check_access_token(token)
    return await role_service.create_role(role.title, role.permissions)


@router.put(
    "/{role_id}/",
    summary="Обновить роль",
    description="Обновить роль",
    status_code=HTTPStatus.OK
)
async def update_role(
    role_id: UUID, role: RoleCreate, token: str,
    auth_service: AuthServiceDep,
    role_service: RoleServiceDep
) -> RoleInDB:
    await auth_service.check_access_token(token)
    return await role_service.update_role(role_id, role.title, role.permissions)


@router.delete(
    "/{role_id}/",
    summary="Удалить роль",
    description="Удалить роль",
    status_code=HTTPStatus.NO_CONTENT
)
async def delete_role(
    role_id: UUID, token: str,
    auth_service: AuthServiceDep,
    role_service: RoleServiceDep
) -> None:
    await auth_service.check_access_token(token)
    await role_service.delete_role(role_id)
