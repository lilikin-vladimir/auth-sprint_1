import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import conint, BaseModel
from pydantic_settings import BaseSettings

load_dotenv()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppConfig(BaseSettings, BaseModel):
    # Название проекта. Используется в Swagger-документации
    project_name: str = 'movies'
    app_host: str = '127.0.0.1'
    app_port: conint(ge=1, le=65535) = 8080
    # настройки redis
    redis_host: str = '127.0.0.1'
    redis_port: conint(ge=1, le=65535) = 6379
    cache_expire_time: conint(ge=0) = 300  # в секундах
    # настройки postgres
    postgres_db_dns: str = 'postgresql+asyncpg://app:123qwe@127.0.0.1:5432/movies_project'
    postgres_echo: bool = True
    auth_schema: str = 'auth'

    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_default_handlers: list[str] = ['console', 'file']
    log_level: Literal['DEBUG', 'ERROR', 'WARNING', 'CRITICAL', 'INFO', 'FATAL'] = 'DEBUG'
    log_file: str = 'test.log'


    class Config:
        env_file = f'{BASE_DIR}/.env'
        env_file_encoding = 'utf-8'


class Crypt(BaseSettings):
    token_name: str = 'X-Bearer_token'
    secret_key: str = 'secret_key'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30  # минуты
    cookie_max_age: int = 1800  # секунды
    # Для паролей
    hashing_method: str = 'PBKDF2'
    hashing_salt_length: int = 16

    class Config:
        env_file = f'{BASE_DIR}/.env'
        env_file_encoding = 'utf-8'
        extra = 'allow'


security_config = Crypt()
config = AppConfig()
