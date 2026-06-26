from uuid import UUID
from pydantic import BaseModel


class CreateGroup(BaseModel):
    title: str
    description: str | None = None
    avatar_url: str | None = None
    is_private: bool


class CreateGroupWithMembers(BaseModel):
    group: CreateGroup
    members: list[UUID]


class GroupResponse(BaseModel):
    title: str
    is_private: bool

    class Config:
        from_attributes = True