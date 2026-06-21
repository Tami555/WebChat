from uuid import UUID
from pydantic import BaseModel
from .messages import ShortMessage


class Chat(BaseModel):
    id: UUID
    title: str
    avatar_url: str | None
    last_message: ShortMessage | None
    unread_count_message: int


class AllChats(BaseModel):
    dialogs: list[Chat]
    groups: list[Chat]