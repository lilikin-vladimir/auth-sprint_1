from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, pwd_context
from models.history import LoginHistory
from models.roles import Role, UserRole
from schemas.users import UserInDB, UserForUpdate
from services.exceptions import role_not_found
from services.database import get_db_service


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, _id: str = None,
                       email: str = None) -> UserInDB:
        async with self.db:
            if _id:
                user_exists = await self.db.execute(
                    select(User).
                    where(User.id == _id))
            elif email:
                user_exists = await self.db.execute(
                    select(User).
                    where(User.email == email))
            else:
                raise AttributeError("id and email is None")
            user = user_exists.scalars().all()
            if user:
                return UserInDB(**jsonable_encoder(user[0]))

    async def authenticate_user(self, username: str,
                                password: str) -> UserInDB | None:
        user = await self.get_user(email=username)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user

    async def add_history(self, user_id: UUID, source: str = None) -> None:
        history = LoginHistory(user_id, source)
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)

    async def update_user_credentials(
            self, user_for_update: UserForUpdate
    ) -> User:
        user_in_db: UserInDB = await self.authenticate_user(
            user_for_update.email, user_for_update.password
        )
        if not user_in_db:
            return None

        user: User = await self.db.get(User, user_in_db.id)
        user.email = user_for_update.new_email
        user.password = pwd_context.hash(user_for_update.new_password)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_paginated_history(self,
                                    user_id: UUID) -> list[LoginHistory]:
        return await paginate(
            self.db,
            (
                select(LoginHistory)
                .where(LoginHistory.user_id == user_id)
                .order_by(LoginHistory.created_at)
            )
        )

    async def get_role(self, user_id: UUID) -> UserRole | None:
        stmt = select(UserRole).where(UserRole.user_id == user_id)
        user_role: UserRole = (await self.db.scalars(stmt)).first()

        if not user_role:
            return None

        return await self.db.get(Role, user_role.role_id)

    async def add_role(self, user_id: UUID, role_id: UUID) -> None:
        role = await self.db.get(Role, role_id)

        if not role:
            raise role_not_found(role_id)

        user_role = await self.get_role(user_id)

        if not user_role:
            user_role = UserRole(user_id=user_id, role_id=role_id)
            self.db.add(user_role)
        else:
            await self.db.execute(
                update(UserRole).where(
                    UserRole.user_id == user_id
                ).values(role_id=role_id)
            )
        await self.db.commit()

    async def remove_role(self, user_id: UUID):
        await self.db.execute(
            delete(UserRole).where(UserRole.user_id == user_id)
        )
        await self.db.commit()


@lru_cache()
def get_user_service(
    db: AsyncSession = Depends(get_db_service),
) -> UserService:
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
