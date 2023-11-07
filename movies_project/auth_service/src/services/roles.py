from uuid import UUID
from functools import lru_cache

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.roles import Role
from services.database import get_db_service
from services.exceptions import role_not_found, role_already_exists


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_roles(self) -> list[Role]:
        roles = await self.db.scalars(select(Role))
        return roles.all()

    async def create_role(self, title: str, permissions: int) -> Role:
        role = (await self.db.execute(select(Role).where(Role.title == title))).one_or_none()
        if role:
            raise role_already_exists

        role = Role(title=title, permissions=permissions)
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def update_role(self, role_id: UUID, title: str, permissions: int) -> Role:
        role = await self.db.get(Role, role_id)

        if not role:
            raise role_not_found(role_id=role_id)

        role.title = title
        role.permissions = permissions
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def delete_role(self, role_id: UUID) -> None:
        role = await self.db.get(Role, role_id)

        if not role:
            raise role_not_found(role_id=role_id)

        await self.db.delete(role)
        await self.db.commit()


@lru_cache()
def get_role_service(
    db: AsyncSession = Depends(get_db_service),
) -> RoleService:
    return RoleService(db)
