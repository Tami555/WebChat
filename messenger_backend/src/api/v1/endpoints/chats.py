from uuid import UUID
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query, UploadFile

import src.api.v1.dependencies as dependencies
from src.core.database import database_helper
from src.models import Users
from src.schemas import (
    AllChatsResponse,
    MessageResponse,
    MessageCreateRequest,
    UploadMessageFileRequest,
)
from src.services import GroupService, DialogService, MessageService, FileService
from src.schemas.enums import ChatType

router = APIRouter()


@router.get("/", response_model=AllChatsResponse)
async def get_user_chats(
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
) -> AllChatsResponse:
    """Получить все чаты пользователя (группы и диалоги)"""
    groups = await GroupService.get_groups_by_user(user=user, session=session)
    dialogs = await DialogService.get_dialogs_by_user(user=user, session=session)
    return AllChatsResponse(dialogs=dialogs, groups=groups)


@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
async def get_chat_messages(
    chat_id: UUID,
    chat_type: Annotated[ChatType, Query],
    page: Annotated[int, Query(gt=0)] = 1,
    limit: Annotated[int, Query(gt=0)] = 50,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Получить сообщения из чата с лимитом"""
    return await MessageService.get_messages_by_chat(
        user=user,
        chat_id=chat_id,
        chat_type=chat_type,
        page=page,
        limit=limit,
        session=session,
    )


@router.post("/messages/create")
async def create_message(
    message_data: MessageCreateRequest = Depends(
        MessageCreateRequest.create_message_by_form
    ),
    message_file: UploadFile | None = None,
    user: Users = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Создание сообщения (для разработки)"""
    if message_file is not None:
        save_file_url = await FileService.upload_message_file(
            upload_data=UploadMessageFileRequest(
                chat_id=message_data.chat_id,
                chat_type=message_data.chat_type,
                file_type=message_data.message_type,
            ),
            upload_file=message_file,
            user=user,
            session=session,
        )
        message_data.file_url = save_file_url
    new_message = await MessageService.create_message(
        user=user, session=session, message_data=message_data
    )
    return {"status": "created", "message_id": new_message.id}
