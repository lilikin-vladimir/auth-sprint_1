from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    redis_host: str = Field('http://127.0.0.1', alias='REDIS_HOST')
    redis_port: str = Field('6379', alias='REDIS_PORT')

    pg_db: str = Field('auth', alias='POSTGRES_DB')
    pg_host: str = Field('127.0.0.1', alias='POSTGRES_HOST')
    pg_port: str = Field('5432', alias='POSTGRES_PORT')
    pg_user: str = Field('postgres', alias='POSTGRES_USER')
    pg_pass: str = Field('postgres', alias='POSTGRES_PASSWORD')

    service_url: str = Field('http://127.0.0.1:8000', alias='AUTH_SERVICE_URL')
    waiters_backoff_max_delay: str = Field('60', alias='BACKOFF_MAX_DELAY')
    waiters_backoff_max_count: str = Field('10', alias='BACKOFF_MAX_COUNT')


settings = Settings()
