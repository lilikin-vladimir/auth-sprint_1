import os
from enum import Enum

from typing import Type

from modules.schemas import UpdatedRow, UpdatedGenre, Movie, Genre, PersonFullInfo, ESSchemaType
from modules.sql_templates import MOVIES_SQL, PERSONS_SQL
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEBUG = os.environ.get('DEBUG', False) == 'True'

POSTGRES_DSN = {
    'host': os.environ.get('POSTGRES_HOST', '127.0.0.1'),
    'port': os.environ.get('POSTGRES_PORT', 5432),
    'dbname': os.environ.get('POSTGRES_DB'),
    'user': os.environ.get('POSTGRES_USER'),
    'password': os.environ.get('POSTGRES_PASSWORD'),
    'options': os.environ.get('POSTGRES_OPTIONS'),
}

ELASTICSEARCH_DSN = {
    'hosts': os.environ.get('ELASTICSEARCH_HOST', 'http://127.0.0.1:9200')
}
ELASTICSEARCH_SCHEMAS_DIR = os.path.join(BASE_DIR, os.environ.get('ELASTICSEARCH_SCHEMAS_DIR', 'data'))

JSON_STATE_PATH = os.path.join(BASE_DIR, os.environ.get('JSON_STATE_PATH', 'data/state.json'))

LIMIT = int(os.environ.get('LIMIT', 50))

SLEEP_TIME = int(os.environ.get('SLEEP_TIME', 5))

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


class UpdatedTable(Enum):
    film_work = UpdatedRow
    genre = UpdatedGenre
    person = UpdatedRow

    def __init__(self, schema: Type[UpdatedRow]) -> None:
        self.schema = schema


class UpdatedTableForMovies(Enum):
    film_work = None, 'fw.id IN %s', UpdatedTable.film_work
    genre = 'LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = ' \
            'fw.id', 'gfw.genre_id IN %s', UpdatedTable.genre
    person = 'LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = ' \
             'fw.id', 'pfw.person_id IN %s', UpdatedTable.person

    def __init__(self, join_sql: str | None, where_sql: str,
                 updated_table: UpdatedTable) -> None:
        self.join_sql = join_sql
        self.where_sql = where_sql
        self.updated_table = updated_table


class UpdatedTableForPersons(Enum):
    person = None, 'p.id IN %s', UpdatedTable.person
    film_work = 'LEFT JOIN content.person_film_work pfw ON pfw.person_id = ' \
                'p.id', 'pfw.film_work_id IN %s', UpdatedTable.film_work

    def __init__(self, join_sql: str | None,
                 where_sql: str, updated_table: UpdatedTable) -> None:
        self.join_sql = join_sql
        self.where_sql = where_sql
        self.updated_table = updated_table


class ESIndexes(Enum):
    movies = 'es_schema_for_movies.json', UpdatedTableForMovies, Movie
    genres = 'es_schema_for_genres.json', UpdatedTable.genre, Genre
    persons = 'es_schema_for_persons.json', UpdatedTableForPersons, PersonFullInfo

    def __init__(self, schema_name: str,
                 updated_table: UpdatedTable | UpdatedTableForMovies | UpdatedTableForPersons,
                 schema: ESSchemaType) -> None:
        self.schema_path = os.path.join(ELASTICSEARCH_SCHEMAS_DIR, schema_name)
        self.updated_table = updated_table
        self.schema = schema


class TransformedTables(Enum):
    movies = *MOVIES_SQL, list(UpdatedTableForMovies), Movie
    persons = *PERSONS_SQL, list(UpdatedTableForPersons), PersonFullInfo

    def __init__(self, start_sql: str, where_template: str, end_sql: str,
                 updated_tables: list[UpdatedTableForMovies | UpdatedTableForPersons],
                 schema: ESSchemaType) -> None:
        self.start_sql = start_sql
        self.where_template = where_template
        self.end_sql = end_sql
        self.updated_tables = updated_tables
        self.schema = schema
