from pydantic import BaseModel


class BaseList(BaseModel):
    page_number: int
    page_size: int
    sort: str | None = None

    @property
    def base_search_params(self) -> dict:
        """Преобразовывает параметры page_number, page_size, sort в size, from, sort
        arg = page_number : int- номер страницы
        arg = page_size : int - размер страницы
        arg = sort : str - сортировка по полю первый знак -: 'desc' без 'asc'
        """
        return {
            "size": self.page_size,
            "from": (self.page_number - 1) * self.page_size,
            'sort': [{self.sort.lstrip('-'): "desc" if self.sort.startswith("-") else "asc"}]
        }


class BaseSearch(BaseList):
    query: str | None = None


class FilmsSearch(BaseSearch):
    genre: str | None = None
    person: str | None = None


class PersonsSearch(BaseSearch):
    pass
