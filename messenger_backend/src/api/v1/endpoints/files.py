from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, UploadFile, Response

from src.api.v1.dependencies import get_current_user
from src.core.database import database_helper
from src.models import Users
from src.schemas import (
    UploadMessageFileRequest,
    DownloadMessageFileRequest,
    DeleteMessageFileRequest,
)
from src.services import FileService

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
    save_file_url = await FileService.upload_message_file(
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
    content, content_type, filename = await FileService.download_message_file(
        download_data=download_data,
        user=user,
        session=session,
    )

    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/messages/delete_file")
async def delete_message_file(
    delete_data: DeleteMessageFileRequest,
    user: Users = Depends(get_current_user),
    session: AsyncSession = Depends(database_helper.create_scoped_session),
):
    """Удаление файла сообщения"""
    deleted = await FileService.delete_message_file(
        delete_data=delete_data,
        user=user,
        session=session,
    )
    return {"deleted": deleted}
