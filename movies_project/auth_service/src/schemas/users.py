from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr
from core import config


class UserEmail(BaseModel):
    email: EmailStr


class UserLogin(UserEmail):
    password: str = Field(..., min_length=8, max_length=50)


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


class UserForUpdate(BaseModel):
    email: EmailStr
    new_email: EmailStr
    password: str = Field(..., min_length=8, max_length=50)
    new_password: str = Field(..., min_length=8, max_length=50)


class UserResponseData(UserEmail, UserData):
    id: UUID

    class Config:
        from_attributes = True


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
    source: str | None
    login_time: datetime

    class Config:
        from_attributes = True
