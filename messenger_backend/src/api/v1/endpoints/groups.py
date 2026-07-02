from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

import src.api.v1.dependencies as dependencies
from src.core.database import database_helper
from src.models import Users
from src.schemas import GroupResponse, CreateGroupWithMembers, Chat
from src.services import GroupService


router = APIRouter()


@router.get("/chats", response_model=list[Chat])
async def get_group_chats(
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> list[Chat]:
    """ Получить все чаты-групп пользователя"""
    return await GroupService.get_groups_by_user(user=user, session=session)


@router.post("/create", response_model=GroupResponse)
async def create_group(
    data: CreateGroupWithMembers,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> GroupResponse:
    """Создать группу с участниками"""
    return await GroupService.create_group(creator=user, create_group_data=data, session=session)