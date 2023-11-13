import pytest
import uuid
from aiohttp import ClientResponse
from http import HTTPStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from tests.functional.testdata.users import get_user
from tests.functional.testdata.roles import get_role, Role


pytestmark = pytest.mark.asyncio
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def test_get_roles(get_token, make_request, pg_add_instances):
    response: ClientResponse = await make_request('/api/v1/roles/')
    assert response.status == HTTPStatus.UNAUTHORIZED

    role1, fake_role1 = get_role()
    role2, fake_role2 = get_role()
    role3, fake_role3 = get_role()
    user, fake_user = get_user()
    await pg_add_instances([user, role1, role2, role3])
    token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})
    response: ClientResponse = await make_request('/api/v1/roles/', token=token)
    body = await response.json()

    assert response.status == HTTPStatus.OK
    assert len(body) == 3
    for fake_role in [fake_role1, fake_role2, fake_role3]:
        assert fake_role.__dict__ in body


async def test_create_role(async_session: AsyncSession, get_token, make_request, pg_add_instances):
    response: ClientResponse = await make_request('/api/v1/roles/', method='post')
    assert response.status == HTTPStatus.UNAUTHORIZED

    user, fake_user = get_user()
    await pg_add_instances([user])
    token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})
    data = {'title': 'admin', 'permissions': 10}
    response: ClientResponse = await make_request(
        '/api/v1/roles/', method='post', data=data, token=token
    )
    new_role = (await async_session.execute(select(Role).where(Role.title == data['title']))).first()

    assert response.status == HTTPStatus.CREATED
    assert new_role is not None


async def test_update_role(async_session: AsyncSession, get_token, make_request, pg_add_instances):
    response: ClientResponse = await make_request('/api/v1/roles/', method='post')
    assert response.status == HTTPStatus.UNAUTHORIZED

    user, fake_user = get_user()
    role, fake_role = get_role()
    await pg_add_instances([user, role])
    token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})
    data = {'title': 'new-test-role', 'permissions': 999}
    response: ClientResponse = await make_request(
        f'/api/v1/roles/{fake_role.id}/', method='put', data=data, token=token
    )
    body = await response.json()
    await async_session.refresh(role)

    assert response.status == HTTPStatus.OK
    assert body['title'] == data['title'] == role.title
    assert body['permissions'] == data['permissions'] == role.permissions
    assert body['id'] == fake_role.id == str(role.id)


async def test_delete_role(async_session: AsyncSession, get_token, make_request, pg_add_instances):
    user, fake_user = get_user()
    role, fake_role = get_role()
    await pg_add_instances([user, role])
    token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})

    response: ClientResponse = await make_request(f'/api/v1/roles/{fake_role.id}', method='delete')
    assert response.status == HTTPStatus.UNAUTHORIZED

    response: ClientResponse = await make_request(
        f'/api/v1/roles/{uuid.uuid4()}/', method='delete', token=token
    )
    assert response.status == HTTPStatus.NOT_FOUND

    response: ClientResponse = await make_request(
        f'/api/v1/roles/{fake_role.id}/', method='delete', token=token
    )
    roles = (await async_session.execute(select(Role))).all()
    assert response.status == HTTPStatus.NO_CONTENT
    assert len(roles) == 0
