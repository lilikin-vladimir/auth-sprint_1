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
    # настройки elasticsearch
    elastic_host: str = 'http://127.0.0.1'
    elastic_port: conint(ge=1, le=65535) = 9200
    # в секундах
    cache_expire_time: conint(ge=0) = 300

    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_default_handlers: list[str] = ['console', 'file']
    log_level: Literal['DEBUG', 'ERROR', 'WARNING', 'CRITICAL', 'INFO', 'FATAL'] = 'DEBUG'
    log_file: str = 'test.log'

    # настройки redis
    test_redis_host: str = '127.0.0.1'
    test_redis_port: conint(ge=1, le=65535) = 16379
    # настройки elasticsearch
    test_elastic_host: str = 'http://127.0.0.1'
    test_elastic_port: conint(ge=1, le=65535) = 19200

    class Config:
        env_file = f'{BASE_DIR}/.env'
        env_file_encoding = 'utf-8'


class ErrorMessage(BaseSettings):
    # Ответ при отсутвии данных
    no_film_found: str = 'film not found'
    no_genre_found: str = 'genre not found'
    no_genres_found: str = 'no genres found'
    no_person_found: str = 'person not found'
    no_films_with_person_found: str = 'films with person not found'

    class Config:
        env_file = f'{BASE_DIR}/.env'
        env_file_encoding = 'utf-8'


config = AppConfig()
error_message = ErrorMessage()
