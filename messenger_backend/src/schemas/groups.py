from uuid import UUID
from pydantic import BaseModel


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


class GroupResponse(BaseModel):
    """Схема группы"""

    id: UUID
    title: str
    is_private: bool

    class Config:
        from_attributes = True
