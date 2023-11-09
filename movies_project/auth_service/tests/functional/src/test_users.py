from http import HTTPStatus
import pytest
from aiohttp import ClientResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from tests.functional.testdata.users import init_users, User
from tests.functional.testdata.roles import init_roles, init_user_roles


@pytest.mark.asyncio
async def test_successfully_get_user_roles(async_session: AsyncSession, get_token, make_request, pg_add_instances):
    user = init_users[0]
    role = init_roles[0]
    await pg_add_instances([user])
    await async_session.refresh(user)
    user_id = user.id
    token = await get_token(data={'username': user.email, 'password': 'password0'})

    # role is None
    response: ClientResponse = await make_request(f'/api/v1/users/{user_id}/roles/', token=token)
    body = await response.json()
    assert response.status == HTTPStatus.OK
    assert body is None

    # created role == role from api
    await pg_add_instances([role])
    await async_session.refresh(role)
    role_id = str(role.id)
    permissions = role.permissions
    role_title = role.title

    user_role = init_user_roles[0]
    user_role.user_id = user_id
    user_role.role_id = role_id
    await pg_add_instances([user_role])
    await async_session.refresh(user_role)

    response: ClientResponse = await make_request(f'/api/v1/users/{user_id}/roles/', token=token)
    body = await response.json()
    assert response.status == HTTPStatus.OK
    assert body == {'id': role_id, 'permissions': permissions, 'title': role_title}


@pytest.mark.asyncio
async def test_failed_get_user_roles(async_session: AsyncSession, get_token, make_request, pg_add_instances):
    user = init_users[1]
    await pg_add_instances([user])
    await async_session.refresh(user)

    # invalid user_id in url
    token = await get_token(data={'username': user.email, 'password': 'password1'})
    invalid_user_id = 'invalid_user_id'
    response: ClientResponse = await make_request(f'/api/v1/users/{invalid_user_id}/roles/', token=token)
    assert response.status == HTTPStatus.UNPROCESSABLE_ENTITY

    # 401 Unauthorized
    invalid_user_id = 'invalid_user_id'
    response: ClientResponse = await make_request(f'/api/v1/users/{invalid_user_id}/roles/')
    assert response.status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_roles2(async_session: AsyncSession, get_token, make_request):
    users = (await async_session.execute(select(User))).scalars().all()
    print(users)
    print('test 2')
    assert 3 == 3
