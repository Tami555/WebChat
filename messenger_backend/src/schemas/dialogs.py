import datetime
from uuid import UUID
from pydantic import BaseModel

from .users import ShortUserResponse


class CreateDialogRequest(BaseModel):
    """Схема создания диалога"""

    interlocutor: UUID  # собеседник (user2)


class DialogDetailResponse(BaseModel):
    """Схема диалога (подробная)"""

    user1: ShortUserResponse
    user2: ShortUserResponse
    created_at: datetime.datetime
