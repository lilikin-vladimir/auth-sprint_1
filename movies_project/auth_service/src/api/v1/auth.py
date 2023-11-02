from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from models.users import User
from schemas.users import UserResponseData, UserSignUp
from services.auth import Token, TokenDep, refresh_access_token, \
    add_invalid_access_token_to_cache, create_token
from services.database import DbDep, CacheDep
from services.users import authenticate_user, add_history
from services.exceptions import user_already_exists_exception, \
    wrong_username_or_password_exception

router = APIRouter()


@router.post('/signup',
             response_model=UserResponseData,
             status_code=HTTPStatus.CREATED,
             description="Регистрация нового пользователя",
             response_description="id, email, hashed password")
async def create_user(user_create: UserSignUp, db: DbDep) -> UserResponseData:
    new_user_data = jsonable_encoder(user_create)
    new_user = User(**new_user_data)

    async with db:
        user_exists = await db.execute(
            select(User).filter(User.email == new_user.email))

        if user_exists.scalars().all():
            raise user_already_exists_exception(new_user.email)

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

    return new_user


@router.post("/login",
             response_model=Token,
             status_code=HTTPStatus.OK,
             description="Вход в аккаунт существующего пользователя")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: DbDep,
        cache: CacheDep) -> Token:
    user = await authenticate_user(form_data.username,
                                   form_data.password, db)
    if not user:
        raise wrong_username_or_password_exception

    await add_history(db=db, user_id=user.id)

    token = await create_token({"sub": str(user.id)}, cache)
    return token


@router.post("/logout",
             description="Выход пользователя из аккаунта",
             status_code=HTTPStatus.OK)
async def logout(token: TokenDep, cache: CacheDep) -> None:
    await add_invalid_access_token_to_cache(token, cache)


@router.post("/refresh",
             response_model=Token,
             description="Получить новую пару access/refresh токенов",
             status_code=HTTPStatus.OK)
async def refresh(token: str, cache: CacheDep) -> Token:
    token = await refresh_access_token(token, cache)
    return token
