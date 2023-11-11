from http import HTTPStatus
import pytest
from aiohttp import ClientResponse
from sqlalchemy.ext.asyncio import AsyncSession
from tests.functional.testdata.users import get_user
from tests.functional.testdata.roles import get_role, get_user_role


@pytest.mark.asyncio
async def test_successfully_get_user_roles(get_token, make_request, pg_add_instances):
    # role is None
    user, fake_user = get_user()
    await pg_add_instances([user])
    token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})
    response: ClientResponse = await make_request(f'/api/v1/users/{fake_user.id}/roles/', token=token)
    body = await response.json()
    assert response.status == HTTPStatus.OK
    assert body is None

    # created role == role from api
    role, fake_role = get_role()
    user_role, _ = get_user_role(fake_user.id, fake_role.id)
    await pg_add_instances([role, user_role])

    response: ClientResponse = await make_request(f'/api/v1/users/{fake_user.id}/roles/', token=token)
    body = await response.json()
    assert response.status == HTTPStatus.OK
    assert body == {'id': fake_role.id, 'permissions': fake_role.permissions, 'title': fake_role.title}


@pytest.mark.asyncio
async def test_failed_get_user_roles(async_session: AsyncSession, get_token, make_request, pg_add_instances):
    user, fake_user = get_user()
    await pg_add_instances([user])
    token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})

    # invalid user_id in url
    invalid_user_id = 'invalid_user_id'
    response: ClientResponse = await make_request(f'/api/v1/users/{invalid_user_id}/roles/', token=token)
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

    # 401 Unauthorized
    invalid_user_id = 'invalid_user_id'
    response: ClientResponse = await make_request(f'/api/v1/users/{invalid_user_id}/roles/')
    assert response.status == HTTPStatus.UNAUTHORIZED
