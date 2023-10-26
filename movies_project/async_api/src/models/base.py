from typing import Any

import orjson
from pydantic import BaseModel


class UUIDMixin(BaseModel):
    uuid: str

    def __init__(self, **data: Any) -> None:
        if 'id' in data:
            data['uuid'] = data.pop('id')
        super().__init__(**data)


class FilmInfo(UUIDMixin):
    title: str
    imdb_rating: float


class FullName(UUIDMixin):
    full_name: str


class Name(UUIDMixin):
    name: str


def orjson_dumps(value, *, default) -> Any:
    return orjson.dumps(value, default=default).decode()


class ORJSONMixin(BaseModel):
    class JsonConfig:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
