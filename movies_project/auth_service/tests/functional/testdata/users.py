
import uuid
from datetime import datetime as dt
from dataclasses import dataclass

from faker import Faker

from .pg_models import User


fake = Faker('ru_RU')


@dataclass
class FakeUser():
    email: str
    password: str
    first_name: str
    last_name: str
    disabled: bool = False
    created_at: dt = dt.now()
    id: str = str(uuid.uuid4())


def get_user() -> tuple[User, FakeUser]:
    data = {
        'email': fake.email(),
        'password': fake.password(length=10),
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'id': str(uuid.uuid4())
    }
    return (User(**data), FakeUser(**data))
