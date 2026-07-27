from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

import src.api.v1.dependencies as dependencies
from src.core.database import database_helper
from src.models import Users
from src.schemas import GroupResponse, CreateGroupWithMembersRequest, ChatResponse
from src.services import GroupService

router = APIRouter()


@router.get("/chats", response_model=list[ChatResponse])
async def get_group_chats(
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
) -> list[ChatResponse]:
    """Получить все чаты-групп пользователя"""
    return await GroupService.get_groups_by_user(user=user, session=session)


@router.post("/create", response_model=GroupResponse)
async def create_group(
    data: CreateGroupWithMembersRequest,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Создать группу с участниками"""
    new_group = await GroupService.create_group(
        creator=user,
        create_group_data=data,
        session=session,
    )
    return new_group
