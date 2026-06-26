import datetime
from uuid import UUID
from pydantic import BaseModel

from .users import ShortUserResponse


class CreateDialog(BaseModel):
    interlocutor: UUID  # собеседник (user2)
    

class DialogDetailResponse(BaseModel):
    user1: ShortUserResponse
    user2: ShortUserResponse
    created_at: datetime.datetime