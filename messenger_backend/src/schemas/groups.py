import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator
from fastapi import Form

from src.schemas import UserInGroupResponse, MediaMessagesResponse
from src.schemas.enums import GroupMemberRole


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


class UpdateGroupRequest(BaseModel):
    """Схема редактирования текстовых данных группы (JSON)"""

    title: str | None = (Form(default=None),)
    description: str | None = (Form(default=None),)
    is_private: bool | None = Form(default=None)

    # Валидация: если передали title, он не должен быть пустой строкой
    @field_validator("title")
    def title_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Название не может быть пустым")
        return v


class AddGroupMembersRequest(BaseModel):
    """Схема добавления участников в группу"""

    members: list[UUID]


class UpdateMemberRoleRequest(BaseModel):
    """Схема изменения роли участника"""

    role: GroupMemberRole


class TransferOwnershipRequest(BaseModel):
    """Схема передачи прав создателя группы"""

    new_creator_id: UUID
