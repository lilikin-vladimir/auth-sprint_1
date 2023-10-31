from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select

from models.users import User
from models.history import LoginHistory
from schemas.users import UserInDB
from services.database import DbDep
from services.auth import verify_password


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
