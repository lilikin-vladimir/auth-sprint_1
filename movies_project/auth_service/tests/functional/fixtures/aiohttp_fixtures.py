import pytest
import aiohttp
import pytest_asyncio

from tests.functional.settings import settings


@pytest_asyncio.fixture(scope='module')
async def aiohttp_session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.fixture(scope='module')
def get_token(aiohttp_session: aiohttp.ClientSession):
    async def inner(data):
        url = settings.service_url + '/api/v1/auth/login'
        headres = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        async with aiohttp_session.post(url=url, headers=headres, data=data) as response:
            body = await response.json()
            return body.get('access_token')
    return inner


@pytest.fixture(scope='module')
def make_request(aiohttp_session: aiohttp.ClientSession):
    request_type: dict[aiohttp.client.ClientRequest] = {
        'get': aiohttp_session.get,
        'post': aiohttp_session.post,
        'put': aiohttp_session.put,
        'delete': aiohttp_session.delete,
    }

    async def inner(url, method='get', params={}, data={}, token=None):
        url = settings.service_url + url
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        async with request_type[method.lower()](url, params=params, json=data, headers=headers) as response:
            await response.json()
            return response

    return inner
