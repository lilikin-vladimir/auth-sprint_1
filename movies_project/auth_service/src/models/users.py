import uuid
from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy import (
    Column, String, DateTime,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID

from db.postgres import Base

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self,
                 email: str,
                 password: str,
                 first_name: str = None,
                 last_name: str = None,
                 disabled: bool = False) -> None:
        self.email = email
        self.password = pwd_context.hash(password)
        self.first_name = first_name if first_name else ''
        self.last_name = last_name if last_name else ''
        self.disabled = disabled

    def __repr__(self) -> str:
        return f'<User {self.email}>'
