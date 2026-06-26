from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

import src.api.v1.dependencies as dependencies
from src.core.database import database_helper
from src.models import Users
from src.schemas import AllChats
from src.services import GroupService, DialogService


router = APIRouter()


@router.get("/", response_model=AllChats)
async def get_user_chats(
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> AllChats:
    """ Получить все чаты пользователя (группы и диалоги)"""
    groups = await GroupService.get_groups_by_user(user=user, session=session)
    dialogs = await DialogService.get_dialogs_by_user(user=user, session=session)
    return AllChats(
        dialogs=dialogs,
        groups=groups
    )