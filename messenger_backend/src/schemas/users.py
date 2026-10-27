import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.schemas.auth import RegistrationUserRequest
from src.schemas.enums import GroupMemberRole


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


class UserInGroupResponse(BaseModel):
    """Схема пользователя в контексте группы"""

    id: UUID
    username: str
    avatar_url: str | None = None
    is_online: bool
    last_seen: datetime.datetime
    role: GroupMemberRole

    model_config = ConfigDict(from_attributes=True)
