import logging
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User
from services.database import CacheDep, DbDep
from services.users import UserService, UserServiceDep
from services.exceptions import credentials_exception, \
    relogin_exception, invalid_access_token_exception, user_already_exists_exception, \
    wrong_username_or_password_exception
from core.config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class Token(BaseModel):
    access_token: str
    access_token_expires: datetime | int
    refresh_token: str = None
    refresh_token_expires: datetime | int = None
    token_type: str = 'bearer'


class TokenPayload(BaseModel):
    sub: UUID
    exp: datetime | int = None


class AuthService:
    def __init__(self, db: AsyncSession, cache: Redis,
                 user_service: UserService):
        self.db = db
        self.cache = cache
        self.user_service = user_service

    async def create_user(self, new_user: User) -> None:
        async with self.db:
            user_exists = await self.db.execute(
                select(User).filter(User.email == new_user.email))

            if user_exists.scalars().all():
                raise user_already_exists_exception(new_user.email)

            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)

    async def login(self, username: str, password: str) -> Token:
        user = await self.user_service.authenticate_user(username,
                                                         password)
        if not user:
            raise wrong_username_or_password_exception

        await self.user_service.add_history(user_id=user.id)

        token = await self.create_token({"sub": str(user.id)})
        return token

    async def create_token(self, data: dict) -> Token:
        access_token_interval = \
            timedelta(minutes=config.access_token_expire_time)
        refresh_token_interval = \
            timedelta(minutes=config.refresh_token_expire_time)

        access_token_expires = datetime.utcnow() + access_token_interval
        refresh_token_expires = datetime.utcnow() + refresh_token_interval

        to_encode = data.copy()

        to_encode.update({'exp': access_token_expires})
        access_token = jwt.encode(to_encode,
                                  config.secret_key_access,
                                  algorithm=config.algorithm)

        to_encode.update({'exp': refresh_token_expires})
        refresh_token = jwt.encode(to_encode,
                                   config.secret_key_refresh,
                                   algorithm=config.algorithm)

        await self.cache.set(refresh_token,
                             to_encode['sub'],
                             int(config.refresh_token_expire_time * 60))

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires=access_token_expires,
            refresh_token_expires=refresh_token_expires
        )

    @staticmethod
    async def decode_token(token: str, secret_key: str) -> tuple[str, int]:
        try:
            payload = jwt.decode(token, secret_key, algorithms=[config.algorithm])
            token_expire = payload.get('exp')
            sub = payload.get('sub')
            cache_expire = \
                token_expire - int(datetime.timestamp(datetime.now()))
            if sub is None:
                raise credentials_exception
            return sub, cache_expire
        except JWTError:
            raise credentials_exception

    async def check_access_token(
            self, token: Annotated[str, Depends(oauth2_scheme)]
    ) -> Token:
        invalid_token = \
            await self.cache.get(f'invalid-access-token:{token}')
        if invalid_token or token == 'undefined':
            raise credentials_exception

        try:
            payload = jwt.decode(token, config.secret_key_access,
                                 algorithms=[config.algorithm])
            logging.info('Access token is valid')
            return Token(**{"access_token": token,
                            "access_token_expires": payload.get("exp")})
        except ExpiredSignatureError:
            raise invalid_access_token_exception

    async def refresh_access_token(self, refresh_token: str) -> Token:
        try:
            jwt.decode(refresh_token, config.secret_key_refresh,
                       algorithms=[config.algorithm])
        except JWTError:
            raise relogin_exception

        user_id = await self.cache.get(refresh_token)
        if not user_id:
            raise relogin_exception

        await self.cache.delete(refresh_token)

        token = await self.create_token({"sub": str(user_id, 'utf-8')})
        return token

    async def add_invalid_access_token_to_cache(self, token: Token) -> None:
        sub, cache_expire = \
            await self.decode_token(token.access_token,
                                    config.secret_key_access)
        await self.cache.set(f'invalid-access-token:{token.access_token}',
                             sub, cache_expire)

    async def get_user_id_from_token(self, token: Token) -> UUID:
        user_id, _ = await self.decode_token(token.access_token,
                                             config.secret_key_access)
        return UUID(user_id)


@lru_cache()
def get_auth_service(db: DbDep, cache: CacheDep,
                     user_service: UserServiceDep) -> AuthService:
    return AuthService(db, cache, user_service)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
