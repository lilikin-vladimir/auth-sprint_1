import uuid
from datetime import datetime
from sqlalchemy import (
    MetaData, Column, String, DateTime, Boolean, Integer, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext


Base = declarative_base(metadata=MetaData(schema='auth'))
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class User(Base):
    __tablename__ = 'users'

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(
        self,
        email: str,
        password: str,
        first_name: str = None,
        last_name: str = None,
        disabled: bool = False
    ) -> None:
        self.email = email
        self.password = pwd_context.hash(password)
        self.first_name = first_name if first_name else ''
        self.last_name = last_name if last_name else ''
        self.disabled = disabled


class Role(Base):
    __tablename__ = 'roles'

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    title = Column(String(255), unique=True, nullable=False)
    permissions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, title: str, permissions: int) -> None:
        self.title = title
        self.permissions = permissions


class UserRole(Base):
    __tablename__ = 'users_roles'

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    user_id = Column(UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role_id = Column(UUID, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False)
    user_role_idx = UniqueConstraint('user_id', 'role_id')

    def __init__(self, user_id: UUID, role_id: UUID) -> None:
        self.user_id = user_id
        self.role_id = role_id


class LoginHistory(Base):
    __tablename__ = 'logins_history'

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    user_id = Column(UUID, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    source = Column(String(255), default=None)
    login_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(
        self, user_id: UUID, source: str = None
    ) -> None:
        self.user_id = user_id
        self.source = source
        self.login_time = self.login_time
