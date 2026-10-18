from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, UploadFile

import src.api.v1.dependencies as dependencies
from src.core.database import database_helper
from src.models import Users
from src.schemas import (
    ShortGroupResponse,
    GroupResponse,
    CreateGroupWithMembersRequest,
    ChatResponse,
    UpdateGroupRequest,
)
from src.services import GroupService

router = APIRouter()


@router.get("/chats", response_model=list[ChatResponse])
async def get_group_chats(
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
) -> list[ChatResponse]:
    """Получить все чаты-групп пользователя"""
    return await GroupService.get_groups_by_user(user=user, session=session)


@router.post("/create", response_model=ShortGroupResponse)
async def create_group(
    data: CreateGroupWithMembersRequest = Depends(
        CreateGroupWithMembersRequest.create_group_by_form
    ),
    avatar: UploadFile | None = None,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Создать группу с участниками"""
    new_group = await GroupService.create_group(
        creator=user,
        create_group_data=data,
        avatar=avatar,
        session=session,
    )
    return new_group


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group_by_id(
    group_id: UUID,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
) -> GroupResponse:
    """Получить полную информацию о группе по id"""
    return await GroupService.get_group_detail(user.id, group_id, session)


@router.patch("/{group_id}", response_model=ShortGroupResponse)
async def update_group_info(
    group_id: UUID,
    data: UpdateGroupRequest,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Редактировать название, описание и приватность группы (только админ)"""
    return await GroupService.update_group_info(
        user=user,
        group_id=group_id,
        update_data=data,
        session=session,
    )
