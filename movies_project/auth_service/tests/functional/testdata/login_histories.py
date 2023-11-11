from .pg_models import LoginHistory
from .users import init_users


init_login_histories = [LoginHistory(
    user_id=user.id,
    source=f'{user.first_name} source'
) for user in init_users]
