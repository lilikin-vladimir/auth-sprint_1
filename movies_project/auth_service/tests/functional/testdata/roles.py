from random import randint
from .pg_models import Role, UserRole
from .users import init_users


ROLE_TITLES = ['admins', 'staff', 'user']

init_roles = [Role(
    title=ROLE_TITLES[i],
    permissions=(10 - i)
) for i in range(len(ROLE_TITLES))]


init_user_roles = [UserRole(
    user_id=user.id,
    role_id=init_roles[randint(0, len(ROLE_TITLES) - 1)].id
) for user in init_users]
