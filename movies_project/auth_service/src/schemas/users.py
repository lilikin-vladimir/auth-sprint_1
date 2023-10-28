from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, constr
from core import config

password_pattern = '^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'


class UserEmail(BaseModel):
    email: EmailStr


class UserLogin(UserEmail):
    password: constr(min_length=8,
                     max_length=50,
                     pattern=password_pattern)


class UserData(BaseModel):
    first_name: str = Field(...,
                            description=config.FIRST_NAME_DESC,
                            min_length=3,
                            max_length=50
                            )
    last_name: str = Field(...,
                           description=config.LAST_NAME_DESC,
                           min_length=3,
                           max_length=50)
    disabled: bool = Field(default=False,
                           description=config.USER_DISABLED_DESC)


class UserSignUp(UserLogin, UserData):
    pass


class UserResponseData(UserEmail, UserData):
    id: UUID

    class Config:
        orm_mode = True


class UserInDB(UserEmail, UserData):
    id: UUID
    hashed_password: str = Field(..., alias="password")


class UserRoleCreate(BaseModel):
    user_id: UUID
    role_id: UUID


class UserRoleInDB(UserRoleCreate):
    id: UUID


class UserHistory(BaseModel):
    user_id: UUID
    source: str = None
    login_time: datetime
