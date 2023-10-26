import os

from dotenv import load_dotenv
from pydantic import conint
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class AppConfig(BaseSettings):
    base_url: str = 'http://127.0.0.1:8000/api/v1'

    redis_host: str = '127.0.0.1'
    redis_port: conint(ge=1, le=65535) = 6379

    elastic_host: str = 'http://127.0.0.1'
    elastic_port: conint(ge=1, le=65535) = 9200

    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, '.env.test'), env_file_encoding='utf-8')


config = AppConfig()

