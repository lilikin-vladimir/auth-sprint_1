import json
from contextlib import contextmanager
from json import JSONDecodeError

from elastic_transport import ApiError, TransportError
from elasticsearch import Elasticsearch
from loguru import logger

from .schemas import Movie, Person, Genre, ESSchemaType
from .services import backoff


class ElasticsearchController:

    def __init__(self, dsn: dict) -> None:
        self.dsn = dsn
        self.connect: Elasticsearch | None = None

    @contextmanager
    def connection(self) -> Elasticsearch:
        # Обработка ошибок подключение не требуется, так как библиотека автоматически переустанавливает подключение
        # при повторном вызове методов
        self.connect = Elasticsearch(**self.dsn)
        logger.info('Инициализация elasticsearch завершена')
        yield self.connect
        self.connect.close()
        logger.info('Подключение к elasticsearch закрыто')

    @backoff(exception=(ApiError, TransportError))
    def create_index_if_not_exists(self, index_name: str, file_path: str) -> None:
        try:
            if not self.connect.indices.exists(index=index_name):
                logger.info('Создание индекса в elasticsearch')
                with open(file_path) as f:
                    self.connect.indices.create(index=index_name, body=json.load(f))
                logger.info('Индекс в elasticsearch создан')
        except (ApiError, TransportError) as e:
            logger.warning(f'Ошибка обновлении данных в elasticsearch: {e}. {index_name=}')
            raise  # Чтобы работал backoff
        except FileNotFoundError:
            logger.error(f'Файл со схемой индекса не найден. {index_name=}. {file_path=}')
            raise
        except JSONDecodeError as e:
            logger.error(f'Ошибка парсинга схемы индекса: {e}. {index_name=}. {file_path=}')
            raise
        except Exception as e:
            logger.error(f'Неизвестная ошибка при создании индекса в elasticsearch: {e}. {index_name=}')
            raise

    @backoff()
    def upload_data(self, index_name: str, rows: list[Movie | Person | Genre],
                    schema: ESSchemaType | None = None) -> None:
        try:
            bulk_body = []
            for row in rows:
                bulk_body.append({'index': {'_index': index_name, '_id': row.id}})
                if schema:
                    row = schema.model_validate_json(row.model_dump_json())
                bulk_body.append(row.model_dump())
            logger.debug(f'{bulk_body[:2]=}')
            response = self.connect.bulk(index=index_name, body=bulk_body, filter_path='items.*.error')
            logger.debug(f'{response=}')
            if response.get('errors'):
                errors_items = response.get('items')
                logger.warning(f'Ошибка обновлении данных в elasticsearch. {index_name=}. {errors_items=}')
        except (ApiError, TransportError) as e:
            logger.warning(f'Ошибка обновлении данных в elasticsearch: {e}. {index_name=}')
            raise  # Чтобы работал backoff
        except Exception as e:
            logger.warning(f'Ошибка обработки при обновлении данных elasticsearch: {e}. {index_name=}')
