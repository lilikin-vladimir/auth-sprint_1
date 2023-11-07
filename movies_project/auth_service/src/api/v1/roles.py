from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from schemas.roles import RoleInDB, RoleCreate
from services.auth import TokenDep
from services.roles import RoleService, get_role_service


router = APIRouter()


@router.get(
    "/",
    summary="Получить роли",
    response_model=list[RoleInDB],
    description="Получить список всех ролей",
    status_code=HTTPStatus.OK
)
async def get_all_roles(
    _: TokenDep, role_service: RoleService = Depends(get_role_service)
) -> list[RoleInDB]:
    return await role_service.get_roles()


@router.post(
    "/",
    summary="Создать роль",
    response_model=RoleInDB,
    description="Создать роль",
    status_code=HTTPStatus.CREATED
)
async def create_role(
    role: RoleCreate, _: TokenDep, role_service: RoleService = Depends(get_role_service)
) -> RoleInDB:
    return await role_service.create_role(role.title, role.permissions)


@router.put(
    "/{role_id}/",
    summary="Обновить роль",
    description="Обновить роль",
    status_code=HTTPStatus.OK
)
async def update_role(
    role_id: UUID,
    role: RoleCreate,
    _: TokenDep,
    role_service: RoleService = Depends(get_role_service)
) -> RoleInDB:
    return await role_service.update_role(role_id, role.title, role.permissions)


@router.delete(
    "/{role_id}/",
    summary="Удалить роль",
    description="Удалить роль",
    status_code=HTTPStatus.NO_CONTENT
)
async def delete_role(
    role_id: UUID,
    _: TokenDep,
    role_service: RoleService = Depends(get_role_service)
) -> None:
    await role_service.delete_role(role_id)
