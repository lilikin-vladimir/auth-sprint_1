from uuid import UUID

from fastapi.encoders import jsonable_encoder
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, update, delete

from models.users import User, pwd_context
from models.history import LoginHistory
from models.roles import Role, UserRole
from schemas.users import UserInDB, UserForUpdate
from services.database import DbDep
from services.auth import verify_password
from services.exceptions import role_not_found


async def get_user(db: DbDep,
                   _id: str = None,
                   email: str = None) -> UserInDB:
    async with db:
        if _id:
            user_exists = await db.execute(
                select(User).
                where(User.id == _id))
        elif email:
            user_exists = await db.execute(
                select(User).
                where(User.email == email))
        else:
            raise AttributeError("id and email is None")
        user = user_exists.scalars().all()
        if user:
            return UserInDB(**jsonable_encoder(user[0]))


async def authenticate_user(username: str,
                            password: str,
                            db: DbDep):
    user = await get_user(email=username, db=db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def add_history(db: DbDep,
                      user_id: UUID,
                      source: str = None) -> None:
    history = LoginHistory(user_id, source)
    db.add(history)
    await db.commit()
    await db.refresh(history)


async def update_user_credentials(user_for_update: UserForUpdate, db: DbDep):
    user_in_db: UserInDB = await authenticate_user(
        user_for_update.email, user_for_update.password, db
    )
    if not user_in_db:
        return None

    user: User = await db.get(User, user_in_db.id)
    user.email = user_for_update.new_email
    user.password = pwd_context.hash(user_for_update.new_password)
    await db.commit()
    await db.refresh(user)
    return user


async def get_paginated_history(user_id: UUID, db: DbDep) -> list[LoginHistory]:
    return await paginate(
        db,
        (
            select(LoginHistory)
            .where(LoginHistory.user_id == user_id)
            .order_by(LoginHistory.created_at)
        )
    )


async def get_role(user_id: UUID, db: DbDep) -> UserRole | None:
    stmt = select(UserRole).where(UserRole.user_id == user_id)
    user_role: UserRole = (await db.scalars(stmt)).first()

    if not user_role:
        return None

    return await db.get(Role, user_role.role_id)


async def add_role(user_id: UUID, role_id: UUID, db: DbDep):
    role = await db.get(Role, role_id)

    if not role:
        raise role_not_found(role_id)

    user_role = await get_role(user_id, db)

    if not user_role:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.add(user_role)
    else:
        await db.execute(
            update(UserRole).where(UserRole.user_id == user_id).values(role_id=role_id)
        )
    await db.commit()


async def remove_role(user_id: UUID, db: DbDep):
    await db.execute(delete(UserRole).where(UserRole.user_id == user_id))
    await db.commit()
