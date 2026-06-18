import datetime
from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserResponse(BaseModel):
    first_name: str | None
    username: str
    phone: PhoneNumber
    bio: str | None
    birthday: datetime.datetime | None
    avatar_url: str | None
    last_seen: datetime.datetime | None
    created_at: datetime.datetime | None