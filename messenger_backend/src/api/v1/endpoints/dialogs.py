from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

import src.api.v1.dependencies as dependencies
from src.core.database import database_helper
from src.models import Users
from src.schemas import CreateDialog, DialogDetailResponse, Chat
from src.services import DialogService


router = APIRouter()


@router.get("/chats", response_model=list[Chat])
async def get_dialog_chats(
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> list[Chat]:
    """ Получить все чаты-диалоги пользователя"""
    return await DialogService.get_dialogs_by_user(user=user, session=session)


@router.post("/create", response_model=DialogDetailResponse)
async def create_dialog(
    data: CreateDialog,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session)
) -> DialogDetailResponse:
    """Создать диалог"""
    return await DialogService.create_dialog(creator=user, dialog_data=data, session=session)