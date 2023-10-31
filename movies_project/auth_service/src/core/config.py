import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    # Настройки приложения
    app_name: str = Field(env='APP_NAME', default='movies')
    app_host: str = Field(env='APP_HOST', default='127.0.0.1')
    app_port: int = Field(env='APP_PORT', default=8080)

    # Настройки БД
    db_name: str = Field(env='DB_NAME', default='movies_database')
    db_user: str = Field(env='DB_USER', default='app')
    db_password: str = Field(env='DB_PASSWORD', default='password')
    db_host: str = Field(env='DB_HOST', default='127.0.0.1')
    db_port: int = Field(env='DB_PORT', default=5432)
    db_echo_engine: bool = Field(env='DB_ECHO_ENGINE', default=False)

    # Настройки Redis
    redis_host: str = Field(env='REDIS_HOST', default='127.0.0.1')
    redis_port: int = Field(env='REDIS_PORT', default=6379)
    cache_expire_time: int = Field(env='REDIS_EXPIRE_TIME', default=300)

    # Настройки аутентификации
    secret_key_access: str = Field(
        env='SECRET_KEY_ACCESS', default='secret'
    )
    secret_key_refresh: str = Field(
        env='SECRET_KEY_REFRESH', default='secret'
    )
    algorithm: str = Field(env='ALGORITHM', default='HS256')
    access_token_expire_time: int = Field(
        env='ACCESS_TOKEN_EXPIRE_TIME', default=15
    )  # в минутах
    refresh_token_expire_time: int = Field(
        env='REFRESH_TOKEN_EXPIRE_TIME', default=7 * 24 * 60
    )  # в минутах

    # Настройки суперпользователя
    admin_email: str = Field(env='ADMIN_EMAIL', default='admin@example.com')
    admin_password: str = Field(env='ADMIN_PASSWORD', default='Password123')

    class Config:
        env_file = '.env'


config = Settings()


ROLE_TITLE_DESC = 'Roles title'
PERMISSIONS_DESC = 'Permission for the role'
FIRST_NAME_DESC = 'User\'s first name'
LAST_NAME_DESC = 'User\'s last name'
USER_DISABLED_DESC = 'True - inactive, False - active'
