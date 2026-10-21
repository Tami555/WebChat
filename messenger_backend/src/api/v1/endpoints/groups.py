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
    AddGroupMembersRequest,
    UpdateMemberRoleRequest,
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


@router.delete("/{group_id}")
async def delete_group(
    group_id: UUID,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Полностью удалить группу (только создатель)"""
    deleted_messages = await GroupService.delete_group(user, group_id, session)
    return {"status": "ok", "deleted_messages": deleted_messages}


@router.post("/{group_id}/members")
async def add_group_members(
    group_id: UUID,
    data: AddGroupMembersRequest,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Добавить участников в группу"""
    await GroupService.add_members(user, group_id, data, session)
    return {"status": "ok"}


@router.delete("/{group_id}/members/{target_user_id}")
async def remove_group_member(
    group_id: UUID,
    target_user_id: UUID,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Удалить участника из группы"""
    await GroupService.remove_member(user, group_id, target_user_id, session)
    return {"status": "ok"}


@router.put("/{group_id}/members/{target_user_id}/role")
async def update_group_member_role(
    group_id: UUID,
    target_user_id: UUID,
    data: UpdateMemberRoleRequest,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Изменить роль участника группы"""
    await GroupService.update_member_role(user, group_id, target_user_id, data, session)
    return {"status": "ok"}


@router.post("/{group_id}/join")
async def join_group(
    group_id: UUID,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Присоединиться к публичной группе"""
    await GroupService.join_public_group(user, group_id, session)
    return {"status": "ok"}


@router.delete("/{group_id}/leave")
async def leave_group(
    group_id: UUID,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Выйти из группы"""
    await GroupService.leave_group(user, group_id, session)
    return {"status": "ok"}
