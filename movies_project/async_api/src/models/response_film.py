from models.base import FullName, Name, FilmInfo


class FilmFullInfoResponse(FilmInfo):
    description: str
    genres: list[Name]
    actors: list[FullName]
    writers: list[FullName]
    directors: list[FullName]
