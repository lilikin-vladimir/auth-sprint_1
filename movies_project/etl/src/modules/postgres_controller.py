from contextlib import contextmanager

import psycopg2
import pydantic
from loguru import logger
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor

from .schemas import Schema, SchemaType
from .services import backoff


class PostgresController:

    def __init__(self, dsn: dict) -> None:
        self.dsn = dsn
        self.connect: connection | None = None

    @backoff()
    def new_connection(self) -> connection:
        try:
            logger.info('Подключение к postgres')
            self.connect = psycopg2.connect(**self.dsn, cursor_factory=RealDictCursor)
            logger.info('Подключение к postgres установлено')
        except psycopg2.OperationalError as e:
            logger.warning(f'Ошибка подключения к postgres: {e}.')
            raise  # Чтобы работал backoff
        return self.connect

    @contextmanager
    def connection(self) -> connection:
        yield self.new_connection()
        if self.connect and not self.connect.closed:
            self.connect.close()
            logger.info('Подключение к postgres закрыто')

    @backoff()
    def fetchall(self, query: str, query_params: tuple | None = None,
                 schema: SchemaType = None) -> list[Schema | dict]:
        try:
            if not self.connect or self.connect.closed:
                self.new_connection()
            with self.connect as connect, connect.cursor() as cursor:
                if query_params:
                    cursor.execute(f'{query};', query_params)
                else:
                    cursor.execute(f'{query};')
                rows = cursor.fetchall()  # Обоснование использования описано в README
                logger.debug(f'{rows[:1]=}')
                if schema:
                    return [schema(**dict(row)) for row in rows]
                return [dict(row) for row in rows]
        except psycopg2.Error as e:
            logger.warning(f'Ошибка при получения данных из postgres: {e}. {query=}')
            raise  # Чтобы работал backoff
        except pydantic.ValidationError as e:
            logger.error(f'Ошибка валидации данных из таблицы postgres: {e}. {query=}. {schema=}')
            return []
        except Exception as e:
            logger.error(f'Ошибка обработки данных из таблицы postgres: {e}. {query=}. {schema=}')
            return []
