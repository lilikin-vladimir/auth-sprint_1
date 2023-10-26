from models.base import FullName, UUIDMixin


class Films(UUIDMixin):
    roles: list[str]


class PersonInfoResponse(FullName):
    films: list[Films]
