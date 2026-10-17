import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from fastapi import Form

from src.schemas import UserInGroupResponse, MediaMessagesResponse


class CreateGroupWithMembersRequest(BaseModel):
    """Схема создания группы с участниками"""

    title: str
    description: str | None = None
    is_private: bool
    members: list[UUID]

    @staticmethod
    def create_group_by_form(
        title: str = Form(...),
        description: str | None = Form(default=None),
        is_private: bool = Form(...),
        members: list[UUID] = Form(default=[]),
    ) -> "CreateGroupWithMembersRequest":

        return CreateGroupWithMembersRequest(
            title=title, description=description, is_private=is_private, members=members
        )


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
