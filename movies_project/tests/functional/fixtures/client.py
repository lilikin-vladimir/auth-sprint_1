from dataclasses import dataclass

import aiohttp
import pytest_asyncio
from aiohttp import ClientSession
from aiohttp.client_exceptions import ContentTypeError

from ..config import config


@pytest_asyncio.fixture(scope='session')
async def client_session() -> aiohttp.ClientSession:
    """Создадим экземпляр сессии aiohttp, для всей сессии."""
    async with aiohttp.ClientSession() as session:
        yield session


@dataclass
class Response:
    status_code: int
    _json: dict

    def json(self) -> dict:
        return self._json


class AsyncClient:

    def __init__(self, base_url: str, session: ClientSession) -> None:
        self.base_url = base_url.rstrip('/')
        self.session = session

    async def get(self, path: str, params: dict | None = None) -> Response:
        url = self.base_url + '/' + path.lstrip('/')
        async with self.session.get(url=url, params=params, allow_redirects=True) as response:
            print(f'{url=}')
            try:
                result = await response.json()
            except (ContentTypeError, Exception):
                return Response(_json={}, status_code=response.status)
            return Response(_json=result, status_code=response.status)


@pytest_asyncio.fixture
async def async_client(client_session: aiohttp.ClientSession) -> AsyncClient:
    return AsyncClient(base_url=config.base_url, session=client_session)
