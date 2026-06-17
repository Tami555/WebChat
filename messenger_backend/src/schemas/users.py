import datetime
from typing import Annotated, Union, Optional
from pydantic import BaseModel, Field
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator


class UserCreate(BaseModel):
    username: str
    phone: Annotated[Union[str, PhoneNumber], PhoneNumberValidator(default_region='RU')]


class UserLogin(BaseModel):
    phone: Annotated[Union[str, PhoneNumber], PhoneNumberValidator(default_region='RU')]


class UserResponse(BaseModel):
    first_name: str | None
    username: str
    phone: PhoneNumber
    bio: str | None
    birthday: datetime.datetime | None
    avatar_url: str | None
    last_seen: datetime.datetime | None
    created_at: datetime.datetime | None