import datetime
from pydantic import BaseModel

from .enums import MessageTypes
from .users import ShortUserResponse


class ShortMessage(BaseModel):
    type: MessageTypes = MessageTypes.TEXT
    created_at: datetime.datetime
    sender: ShortUserResponse
    content: str | None = None

    class Config:
        from_attributes = True

