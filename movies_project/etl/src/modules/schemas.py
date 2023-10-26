from datetime import datetime
from typing import Type
from uuid import UUID

from pydantic import BaseModel
from pydantic.fields import Field


class UUIDMixin:
    class Config:
        json_encoders = {
            UUID: str
        }


class UpdatedRow(BaseModel, UUIDMixin):
    id: UUID | None = None
    updated_at: datetime | None = None


class UpdatedGenre(UpdatedRow):
    name: str


class UploadedRow(BaseModel, UUIDMixin):
    id: UUID | None = None
    updated_row_by_table_name: dict[str, UpdatedRow | None] = Field(default_factory=dict)


class Person(BaseModel):
    id: str
    full_name: str


class FilmRoles(BaseModel):
    id: str
    roles: list[str]


class PersonFullInfo(Person):
    films: list[FilmRoles]


class Genre(BaseModel):
    id: str
    name: str


class Movie(BaseModel):
    id: str
    title: str
    description: str
    imdb_rating: float
    genres_names: list[str]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]
    genres: list[Genre]


Schema = UpdatedRow | Movie

SchemaType = Type[UpdatedRow] | Type[Movie]

ESSchemaType = Type[Movie] | Type[Genre] | Type[Person]
