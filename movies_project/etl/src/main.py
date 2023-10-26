import sys
import time
from uuid import UUID

from loguru import logger

from modules.config import (
    DEBUG,
    POSTGRES_DSN,
    ELASTICSEARCH_DSN,
    JSON_STATE_PATH,
    SLEEP_TIME,
    LOG_LEVEL,
    UpdatedTable,
    ESIndexes,
    TransformedTables
)
from modules.elasticsearch_controller import ElasticsearchController
from modules.extractors import Extractor
from modules.postgres_controller import PostgresController

if not DEBUG:
    logger.remove()
    logger.add(sys.stderr, level=LOG_LEVEL)


def main() -> None:
    logger.info('Запустился')
    postgres_controller = PostgresController(dsn=POSTGRES_DSN)
    elasticsearch_controller = ElasticsearchController(dsn=ELASTICSEARCH_DSN)
    with postgres_controller.connection(), elasticsearch_controller.connection():
        for elasticsearch_index in ESIndexes:
            elasticsearch_controller.create_index_if_not_exists(index_name=elasticsearch_index.name,
                                                                file_path=elasticsearch_index.schema_path)
        extractor = Extractor(updated_tables=list(UpdatedTable), transformed_tables=list(TransformedTables),
                              json_state_path=JSON_STATE_PATH, database_controller=postgres_controller)
        while True:
            updated_rows_by_table = extractor.updates.get_updated_rows()
            if not any(updated_rows_by_table.values()):
                time.sleep(SLEEP_TIME)
                continue

            for elasticsearch_index in ESIndexes:
                if not isinstance(elasticsearch_index.updated_table, UpdatedTable):
                    continue
                rows = updated_rows_by_table.get(elasticsearch_index.updated_table)
                if rows:
                    elasticsearch_controller.upload_data(index_name=elasticsearch_index.name, rows=rows,
                                                         schema=elasticsearch_index.schema)

            last_updated_row_by_table_name = {table.name: rows[-1] if rows else None
                                              for table, rows in updated_rows_by_table.items()}

            for transformed_extractor in extractor.transformed_tables_extractor:
                transformed_extractor.refresh_state()
                while True:
                    updated_data = transformed_extractor.get_rows_for_update(
                        updated_rows_by_table=updated_rows_by_table)
                    if not updated_data:
                        break
                    elasticsearch_controller.upload_data(index_name=transformed_extractor.table_data.name,
                                                         rows=updated_data)

                    # Запоминаем состояние на случай прерывания скрипта
                    transformed_extractor.update_state(last_uploaded_id=UUID(updated_data[-1].id),
                                                       last_updated_row_by_table_name=last_updated_row_by_table_name)

            # Запоминаем, какие обновлённые записи были обработаны
            extractor.updates.save_state(last_updated_row_by_table_name=last_updated_row_by_table_name)


if __name__ == '__main__':
    main()
