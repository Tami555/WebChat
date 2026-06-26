import datetime
from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber


class ShortUserResponse(BaseModel):
    username: str
    phone: PhoneNumber
    avatar_url: str | None = None

    class Config:
        from_attributes = True


class UserResponse(ShortUserResponse):
    first_name: str | None
    bio: str | None
    birthday: datetime.datetime | None
    last_seen: datetime.datetime | None
    created_at: datetime.datetime | None