from uuid import UUID
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query

import src.api.v1.dependencies as dependencies
from src.core.database import database_helper
from src.models import Users
from src.schemas import AllChats, MessageResponse
from src.services import GroupService, DialogService, MessageService
from src.schemas.enums import ChatTypes


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


@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
async def get_chat_messages(
    chat_id: UUID,
    chat_type: Annotated[ChatTypes, Query],
    page: Annotated[int, Query] = 1,
    limit: Annotated[int, Query] = 50,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> list[MessageResponse]:
    """ Получить сообщения из чата с лимитом"""
    return await MessageService.get_messages_by_chat(
        user=user,
        chat_id=chat_id,
        chat_type=chat_type,
        page=page,
        limit=limit,
        session=session
    )