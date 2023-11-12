import uuid
from dataclasses import dataclass

from faker import Faker

from .pg_models import LoginHistory


fake = Faker('ru_RU')


@dataclass
class FakeLoginHistory():
    user_id: str
    source: str
    id: str = str(uuid.uuid4())


def get_login_history(user_id: str = str(uuid.uuid4())) -> tuple[LoginHistory, FakeLoginHistory]:
    data = {
        'user_id': str(user_id),
        'source': fake.slug(),
        'id': str(uuid.uuid4())
    }
    return (LoginHistory(**data), FakeLoginHistory(**data))
