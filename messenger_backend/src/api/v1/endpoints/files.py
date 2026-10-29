from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, UploadFile, Response
from urllib.parse import quote

from src.api.v1.dependencies import get_current_user
from src.core.database import database_helper
from src.models import Users
from src.schemas import (
    UploadMessageFileRequest,
    DownloadMessageFileRequest,
    DeleteMessageFileRequest,
    ShortGroupResponse,
)
from src.services import MessageService, GroupService

router = APIRouter()


@router.post("/messages/upload_file")
async def upload_message_file(
    upload_file: UploadFile,
    upload_data: UploadMessageFileRequest = Depends(
        UploadMessageFileRequest.upload_message_file_by_form
    ),
    user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Загрузка файла сообщения"""
    save_file_url = await MessageService.upload_message_file(
        upload_data=upload_data,
        upload_file=upload_file,
        user=user,
        session=session,
    )
    return {"file_url": save_file_url}


@router.post("/messages/download_file")
async def download_message_file(
    download_data: DownloadMessageFileRequest,
    user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Скачивание файла сообщения"""
    content, content_type, filename = await MessageService.download_message_file(
        download_data=download_data,
        user=user,
        session=session,
    )
    encoded_filename = quote(filename, encoding="utf-8")
    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{encoded_filename}"'},
    )


@router.delete("/messages/delete_file")
async def delete_message_file(
    delete_data: DeleteMessageFileRequest,
    user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Удаление файла сообщения"""
    deleted = await MessageService.delete_message_file(
        delete_data=delete_data,
        user=user,
        session=session,
    )
    return {"deleted": deleted}


@router.put("/groups/{group_id}/avatar", response_model=ShortGroupResponse)
async def update_group_avatar(
    group_id: UUID,
    avatar: UploadFile,
    user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Обновить или удалить аву группы"""
    return await GroupService.update_group_avatar(
        user=user,
        group_id=group_id,
        avatar=avatar,
        session=session,
    )


@router.delete("/groups/{group_id}/avatar", response_model=ShortGroupResponse)
async def delete_group_avatar(
    group_id: UUID,
    user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Удалить аватарку группы"""
    return await GroupService.delete_group_avatar(
        user=user,
        group_id=group_id,
        session=session,
    )
