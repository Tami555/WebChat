import datetime
from pydantic import BaseModel

from .enums import MessageTypes
from .users import ShortUserResponse
from .sticker import ShortStickerResponse, StickerResponse


class ShortMessageResponse(BaseModel):
    sender: ShortUserResponse
    type: MessageTypes = MessageTypes.TEXT
    created_at: datetime.datetime
    content: str | None = None
    sticker: ShortStickerResponse | None = None

    class Config:
        from_attributes = True


class MessageResponse(ShortMessageResponse):
    file_url: str | None = None
    sticker: StickerResponse | None = None
    reply_message: ShortMessageResponse | None = None
    is_edited: bool

    class Config:
        from_attributes = True
