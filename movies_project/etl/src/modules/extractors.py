from typing import Type
from uuid import UUID

from loguru import logger

from .config import LIMIT, UpdatedTable, TransformedTables
from .postgres_controller import PostgresController
from .schemas import UpdatedRow, Movie, UploadedRow, PersonFullInfo
from .services import State, JsonFileStorage


class Worker:
    state_schema = UpdatedRow
    type: str = 'worker'

    def __init__(self, table_name: str, state_controller: State,
                 database_controller: PostgresController, limit: int = LIMIT,
                 result_schema: Type[UpdatedRow] = UpdatedRow) -> None:
        self.state_key = f'{table_name}_{self.type}'
        self.table_name = table_name
        self.result_schema = result_schema
        self.database_controller = database_controller
        self.limit = limit
        self.state_controller = state_controller
        state = self.state_controller.get_state(self.state_key, '{}')
        self.state = self.state_schema.model_validate_json(state)

    def save_state(self, last_row: UpdatedRow | None = None) -> None:
        if last_row:
            self.state.updated_at = last_row.updated_at
            self.state.id = last_row.id
        self.state_controller.set_state(self.state_key, self.state.model_dump_json())


class UpdatesExtractor(Worker):
    state_schema = UpdatedRow
    type: str = 'extractor'

    def get_updated_rows(self) -> list[UpdatedRow]:
        query = f"""
        SELECT {", ".join(self.result_schema.model_fields)}
        FROM {self.table_name}
        """
        if self.state.updated_at and self.state.id:
            query += 'WHERE updated_at > %s or (updated_at = %s AND id > %s)'
            query_params = (self.state.updated_at, self.state.updated_at, str(self.state.id), self.limit)
        else:
            query_params = (self.limit,)
        query += """
        ORDER BY updated_at ASC, id ASC
        LIMIT %s;
        """
        logger.debug(f'{query=}')
        logger.debug(f'{query_params=}')
        updated_rows = self.database_controller.fetchall(query=query, query_params=query_params,
                                                         schema=self.result_schema)
        logger.debug(f'Получено {self.table_name}: {len(updated_rows)}. {updated_rows[:1]=}')
        return updated_rows


class TransformExtractor(Worker):
    state_schema = UploadedRow
    state: UploadedRow
    type: str = 'transform_extractor'

    def __init__(self, table_data: TransformedTables,
                 extractors: dict[UpdatedTable, UpdatesExtractor],
                 **kwargs) -> None:
        self.table_data = table_data
        self.extractors = extractors
        super().__init__(table_name=table_data.name, **kwargs)

    def save_state(self, last_row: UploadedRow | None = None):
        if last_row:
            self.state.id = last_row.id
            self.state.updated_row_by_table_name = last_row.updated_row_by_table_name
        self.state_controller.set_state(self.state_key, self.state.model_dump_json())

    def refresh_state(self) -> None:
        for table in self.table_data.updated_tables:
            if self.state.updated_row_by_table_name.get(table.name) != self.extractors[table.updated_table].state:
                self.state = UploadedRow()
                return

    def update_state(
            self, last_uploaded_id: UUID,
            last_updated_row_by_table_name: dict[str, UpdatedRow | None]) -> None:
        last_uploaded_row = UploadedRow(id=last_uploaded_id,
                                        updated_row_by_table_name=last_updated_row_by_table_name)
        self.save_state(last_row=last_uploaded_row)

    def get_rows_for_update(self,
                            updated_rows_by_table: dict[UpdatedTable, list[UpdatedRow] | None]
                            ) -> list[Movie | PersonFullInfo]:
        query = self.table_data.start_sql
        query_params = []
        where = []
        for table in self.table_data.updated_tables:
            updated_rows = updated_rows_by_table.get(table.updated_table)
            if not updated_rows:
                continue
            if table.join_sql:
                query += f'{table.join_sql}\n'
            updated_rows_ids = (str(row.id) for row in updated_rows)
            query_params.append(tuple(updated_rows_ids))  # tuple - чтобы из генератора сделать tuple
            where.append(table.where_sql)
        if not query_params:
            return []
        where_str = ' OR '.join(where)
        if self.state.id:
            where_str = self.table_data.where_template.format(where_str=where_str)
            query_params.insert(0, str(self.state.id))
        query += f'WHERE {where_str}'  # WHERE id > %s AND (fw.id IN %s OR pfw.person_id IN %s OR gfw.genre_id IN %s)
        query += self.table_data.end_sql
        query_params.append(self.limit)
        logger.debug(f'{query=}')
        logger.debug(f'{query_params=}')
        rows_for_update = self.database_controller.fetchall(query=query, query_params=tuple(query_params),
                                                            schema=self.table_data.schema)
        logger.debug(f'{rows_for_update[:1]=}')
        logger.debug(f'Получено {self.table_name}: {len(rows_for_update)}. {rows_for_update[:1]=}')
        return rows_for_update


class UpdatesExtractorsManager:

    def __init__(self, tables: list[UpdatedTable], state_controller: State,
                 database_controller: PostgresController) -> None:
        self.extractors: dict[UpdatedTable, UpdatesExtractor] = {}
        for table in tables:
            self.extractors[table] = UpdatesExtractor(table_name=table.name, state_controller=state_controller,
                                                      database_controller=database_controller,
                                                      result_schema=table.schema)

    def get_updated_rows(self) -> dict[UpdatedTable, list[UpdatedRow]]:
        updated_rows_by_table = {}
        for table, extractor in self.extractors.items():
            updated_rows_by_table[table] = extractor.get_updated_rows()
        return updated_rows_by_table

    def save_state(self, last_updated_row_by_table_name: dict[str, UpdatedRow | None]) -> None:
        for extractor in self.extractors.values():
            extractor.save_state(last_updated_row_by_table_name.get(extractor.table_name))


class Extractor:

    def __init__(self, updated_tables: list[UpdatedTable],
                 transformed_tables: list[TransformedTables],
                 json_state_path: str, database_controller: PostgresController) -> None:
        storage = JsonFileStorage(file_path=json_state_path)
        state_controller = State(storage=storage)
        self.updated_tables = updated_tables
        self.updates = UpdatesExtractorsManager(tables=updated_tables, state_controller=state_controller,
                                                database_controller=database_controller)
        self.transformed_tables_extractor = [
            TransformExtractor(table_data=table, extractors=self.updates.extractors, state_controller=state_controller,
                               database_controller=database_controller)
            for table in transformed_tables]
