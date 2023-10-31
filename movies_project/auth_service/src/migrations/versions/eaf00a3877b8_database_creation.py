"""Database creation

Revision ID: eaf00a3877b8
Revises: 
Create Date: 2023-10-31 17:21:12.950357

"""
from alembic import op

from models.history import LoginHistory
from models.roles import Role, UserRole
from models.users import User

# revision identifiers, used by Alembic.
revision = 'eaf00a3877b8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        User.id.expression,
        User.email.expression,
        User.password.expression,
        User.first_name.expression,
        User.last_name.expression,
        User.disabled.expression,
        User.created_at.expression
    )

    op.create_table(
        'roles',
        Role.id.expression,
        Role.title.expression,
        Role.permissions.expression,
        Role.created_at.expression,
    )

    op.create_table(
        'users_roles',
        UserRole.id.expression,
        UserRole.user_id.expression,
        UserRole.role_id.expression,
        UserRole.user_role_idx
    )

    op.create_table(
        'logins_history',
        LoginHistory.id.expression,
        LoginHistory.user_id.expression,
        LoginHistory.source.expression,
        LoginHistory.login_time.expression,
        LoginHistory.created_at.expression
    )


def downgrade() -> None:
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('users_roles')
    op.drop_table('logins_history')
