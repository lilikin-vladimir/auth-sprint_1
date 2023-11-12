import uuid
from random import randint
from dataclasses import dataclass

from .pg_models import Role, UserRole


ROLE_TITLES = ['admins', 'staff', 'user']


@dataclass
class FakeRole():
    title: str
    permissions: int
    id: str = str(uuid.uuid4())


@dataclass
class FakeUserRole():
    user_id: str
    role_id: int
    id: str = str(uuid.uuid4())


def get_role() -> tuple[Role, FakeRole]:
    data = {
        'title': ROLE_TITLES[randint(0, len(ROLE_TITLES) - 1)],
        'permissions': randint(0, 10),
        'id': str(uuid.uuid4())
    }
    return (Role(**data), FakeRole(**data))


def get_user_role(
    user_id: str = str(uuid.uuid4()), role_id: str = str(uuid.uuid4())
) -> tuple[UserRole, FakeUserRole]:
    data = {
        'user_id': user_id,
        'role_id': role_id,
        'id': str(uuid.uuid4())
    }
    return (UserRole(**data), FakeUserRole(**data))
