import logging
from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from pydantic import BaseModel
from redis.asyncio import Redis
from services.database import CacheDep
from services.exceptions import credentials_exception, \
    relogin_exception, invalid_access_token_exception
from core.config import config


class Token(BaseModel):
    access_token: str
    access_token_expires: datetime | int
    refresh_token: str = None
    refresh_token_expires: datetime | int = None
    token_type: str = 'bearer'


class TokenPayload(BaseModel):
    sub: UUID
    exp: datetime | int = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def create_token(data: dict, cache: CacheDep) -> Token:
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

    await cache.set(refresh_token,
                    to_encode['sub'],
                    int(config.refresh_token_expire_time*60))

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expires=access_token_expires,
        refresh_token_expires=refresh_token_expires
    )


async def decode_token(token: str, secret_key: str) -> tuple[str, str]:
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


async def check_access_token(token: Annotated[str, Depends(oauth2_scheme)],
                             cache: CacheDep):
    invalid_token = await cache.get(f'invalid-access-token:{token}')
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


async def refresh_access_token(refresh_token: str, cache: Redis) -> Token:
    try:
        jwt.decode(refresh_token, config.secret_key_refresh,
                   algorithms=[config.algorithm])
    except JWTError:
        raise relogin_exception

    user_id = await cache.get(refresh_token)
    if not user_id:
        raise relogin_exception

    await cache.delete(refresh_token)

    token = await create_token({"sub": str(user_id, 'utf-8')}, cache)
    return token


async def add_invalid_access_token_to_cache(token: Token,
                                            cache: CacheDep) -> None:
    sub, cache_expire = await decode_token(token.access_token,
                                           config.secret_key_access)
    await cache.set(f'invalid-access-token:{token.access_token}',
                    sub, cache_expire)


async def get_user_id_from_token(token: Token) -> UUID:
    user_id, _ = await decode_token(token.access_token, config.secret_key_access)
    return UUID(user_id)

TokenDep = Annotated[Token, Depends(check_access_token)]
