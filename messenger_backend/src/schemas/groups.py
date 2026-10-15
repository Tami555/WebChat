import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from src.schemas import UserInGroupResponse, MediaMessagesResponse


class CreateGroupRequest(BaseModel):
    """Схема создания группы"""

    title: str
    description: str | None = None
    avatar_url: str | None = None
    is_private: bool


class CreateGroupWithMembersRequest(BaseModel):
    """Схема создания группы с участниками"""

    group: CreateGroupRequest
    members: list[UUID]


class ShortGroupResponse(BaseModel):
    """Схема группы (краткая)"""

    id: UUID
    title: str
    is_private: bool

    model_config = ConfigDict(from_attributes=True)


class GroupResponse(ShortGroupResponse):
    """Схема группы (полная)"""

    description: str | None = None
    avatar_url: str | None = None
    created_at: datetime.datetime
    members: list[UserInGroupResponse]
    media: MediaMessagesResponse
