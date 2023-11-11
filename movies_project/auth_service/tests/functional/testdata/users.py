from .pg_models import User


init_users = [User(
    email=f'user{i}@email.com',
    password=f'password{i}',
    first_name=f'first{i}',
    last_name=f'last{i}'
) for i in range(5)]
