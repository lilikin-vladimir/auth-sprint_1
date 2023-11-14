from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm

from models.users import User
from schemas.users import UserResponseData, UserSignUp
from services.auth import Token, AuthServiceDep

router = APIRouter()


@router.post('/signup',
             response_model=UserResponseData,
             status_code=HTTPStatus.CREATED,
             description="Регистрация нового пользователя",
             response_description="id, email, hashed password")
async def create_user(user_create: UserSignUp,
                      auth_service: AuthServiceDep) -> UserResponseData:
    new_user_data = jsonable_encoder(user_create)
    new_user = User(**new_user_data)
    await auth_service.create_user(new_user)
    return new_user


@router.post("/login",
             response_model=Token,
             status_code=HTTPStatus.OK,
             description="Вход в аккаунт существующего пользователя")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: AuthServiceDep) -> Token:
    token = await auth_service.login(form_data.username,
                                     form_data.password)
    return token


@router.post("/logout",
             description="Выход пользователя из аккаунта",
             status_code=HTTPStatus.OK)
async def logout(token: str, auth_service: AuthServiceDep) -> None:
    token = await auth_service.check_access_token(token)
    await auth_service.add_invalid_access_token_to_cache(token)


@router.post("/refresh",
             response_model=Token,
             description="Получить новую пару access/refresh токенов",
             status_code=HTTPStatus.OK)
async def refresh(token: str, auth_service: AuthServiceDep) -> Token:
    token = await auth_service.refresh_access_token(token)
    return token
