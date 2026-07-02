from uuid import UUID
from pydantic import BaseModel
from .messages import ShortMessageResponse


class Chat(BaseModel):
    id: UUID
    title: str
    avatar_url: str | None
    last_message: ShortMessageResponse | None
    unread_count_message: int


class AllChats(BaseModel):
    dialogs: list[Chat]
    groups: list[Chat]