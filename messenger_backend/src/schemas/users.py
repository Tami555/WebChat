import datetime
from pydantic import BaseModel, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.schemas.auth import RegistrationUserRequest


class ShortUserResponse(BaseModel):
    """Схема пользователя (не полная)"""

    username: str
    phone: PhoneNumber
    avatar_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(ShortUserResponse):
    """Схема пользователя"""

    first_name: str | None
    bio: str | None
    birthday: datetime.datetime | None
    last_seen: datetime.datetime | None
    created_at: datetime.datetime | None


class CreateUserRequest(RegistrationUserRequest):
    """Схема создания пользователя"""

    last_seen: datetime.datetime | None
