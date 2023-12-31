import pytest
import uuid
from aiohttp import ClientResponse
from http import HTTPStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from tests.functional.testdata.users import get_user
from tests.functional.testdata.roles import get_role, get_user_role, UserRole


pytestmark = pytest.mark.asyncio
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


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


async def test_failed_get_user_roles(get_token, make_request, pg_add_instances):
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


async def test_successfully_set_user_role(get_token, make_request, pg_add_instances):
    user, fake_user = get_user()
    role, fake_role = get_role()

    await pg_add_instances([user, role])
    token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})
    response: ClientResponse = await make_request(
        f'/api/v1/users/{fake_user.id}/roles/', method='post', data={'role_id': fake_role.id}, token=token
    )
    body = await response.json()
    assert response.status == HTTPStatus.NO_CONTENT
    assert body is None


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'role_id': str(uuid.uuid4())},
            {'status': HTTPStatus.NOT_FOUND}
        ),
        (
            {'role': str(uuid.uuid4())},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
            {},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
    ]
)
async def test_failed_set_user_role(
    get_token, make_request, pg_add_instances, query_data: dict, expected_answer: dict
):
    user, fake_user = get_user()
    await pg_add_instances([user])
    token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})
    response: ClientResponse = await make_request(
        f'/api/v1/users/{fake_user.id}/roles/', method='post', data=query_data, token=token
    )

    assert response.status == expected_answer['status']


async def test_delete_user_role(
    async_session: AsyncSession, get_token, make_request, pg_add_instances
):
    user, fake_user = get_user()
    role, fake_role = get_role()
    user_role, _ = get_user_role(fake_user.id, fake_role.id)

    # successfully_delete
    await pg_add_instances([user, role, user_role])
    token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})
    response: ClientResponse = await make_request(
        f'/api/v1/users/{fake_user.id}/roles/', method='delete', token=token
    )
    await async_session.refresh(user)
    user_roles = (
        await async_session.execute(select(UserRole).where(UserRole.user_id == fake_user.id))
    ).all()
    assert response.status == HTTPStatus.NO_CONTENT
    assert user_roles == []

    # role not found
    response: ClientResponse = await make_request(
        f'/api/v1/users/{fake_user.id}/roles/', method='delete', token=token
    )
    assert response.status == HTTPStatus.NO_CONTENT


@pytest.mark.parametrize(
    'page, size, login_count, pages',
    [
        (1, 30, 1, 1),
        (2, 2, 10, 10 / 2),
        (1, 50, 3, 1),
    ]
)
async def test_successfully_get_login_histories(
    get_token, make_request, pg_add_instances,
    page, size, login_count, pages,
):
    user, fake_user = get_user()
    await pg_add_instances([user])

    for _ in range(login_count):
        token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})

    response: ClientResponse = await make_request(
        f'/api/v1/users/{fake_user.id}/auth-history/',
        params={'page': page, 'size': size},
        token=token
    )
    body = await response.json()

    assert response.status == HTTPStatus.OK
    assert body.get('total') == login_count
    assert body.get('page') == page
    assert body.get('size') == size
    assert body.get('pages') == (1 if login_count <= size else login_count / size)
    assert isinstance(body.get('items'), list)
    assert len(body.get('items')) == (login_count if size >= login_count else size)
    for i in body.get('items'):
        assert i['user_id'] == fake_user.id


async def test_successfully_update_creds(
    async_session: AsyncSession, get_token, make_request, pg_add_instances
):
    user, fake_user = get_user()
    await pg_add_instances([user])
    token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})
    new_email = 'new-email-for-test@email.com'
    new_passsword = 'new-password-for-test'
    data = {
        'email': fake_user.email,
        'new_email': new_email,
        'password': fake_user.password,
        'new_password': new_passsword,
    }
    response: ClientResponse = await make_request(
        '/api/v1/users/update-credentials/', method='put', data=data, token=token
    )
    await async_session.refresh(user)

    assert response.status == HTTPStatus.OK
    assert user.email == new_email
    assert pwd_context.verify(new_passsword, user.password) is True


@pytest.mark.parametrize(
    'query_data, expected_status',
    [
        (
            {'email': 'undefined-email@email.com'},
            HTTPStatus.UNAUTHORIZED
        ),
        (
            {'password': 'invalid-password'},
            HTTPStatus.UNAUTHORIZED
        ),
        (
            {'new_password': '1234567'},
            HTTPStatus.UNPROCESSABLE_ENTITY
        ),
    ]
)
async def test_failed_update_creds(
    get_token, make_request, pg_add_instances,
    query_data: dict, expected_status: int,
):
    user, fake_user = get_user()
    await pg_add_instances([user])
    token = await get_token(data={'username': fake_user.email, 'password': fake_user.password})
    data = {
        'email': fake_user.email,
        'new_email': 'new-email-for-test@email.com',
        'password': fake_user.password,
        'new_password': 'new-password-for-test',
    }
    data.update(query_data)
    response: ClientResponse = await make_request(
        '/api/v1/users/update-credentials/', method='put', data=data, token=token
    )

    assert response.status == expected_status
