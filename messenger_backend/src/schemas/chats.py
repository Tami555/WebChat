from uuid import UUID
from pydantic import BaseModel
from .messages import ShortMessageResponse


class ChatResponse(BaseModel):
    """Схема чата"""

    id: UUID
    title: str
    avatar_url: str | None
    last_message: ShortMessageResponse | None
    unread_count_message: int


class AllChatsResponse(BaseModel):
    """Схема чатов всех типов"""

    dialogs: list[ChatResponse]
    groups: list[ChatResponse]
