from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from pathlib import Path

from src.schemas import (
    UploadMessageFileRequest,
    DownloadMessageFileRequest,
    DeleteMessageFileRequest,
)
from src.models import Users
from src.utils.files import get_file_type_for_message, get_file_manager, FilePathHelper
from src.exceptions import NotCorrectMessageTypeForFileTypeError
from src.services import MessageService


class FileService:
    """Сервис для работы с файлами"""

    @staticmethod
    async def upload_message_file(
        upload_data: UploadMessageFileRequest,
        upload_file: UploadFile,
        user: Users,
        session: AsyncSession,
    ):
        """Проверка корректности и загрузка файла сообщения"""
        # Проверка, что отправитель является участником чата
        await MessageService.check_user_is_member(
            user_id=user.id,
            chat_id=upload_data.chat_id,
            chat_type=upload_data.chat_type,
            session=session,
        )

        # Проверка на тип сообщения и тип файла
        real_file_type = get_file_type_for_message(upload_file.content_type)
        if real_file_type != upload_data.file_type:
            raise NotCorrectMessageTypeForFileTypeError(
                upload_data.file_type, upload_file.content_type
            )

        # Сохраняем файл
        file_manager = get_file_manager()
        file_path = FilePathHelper.generate_message_file_path(
            chat_id=upload_data.chat_id,
            file_type=upload_data.file_type,
            username=user.username,
            filename=upload_file.filename,
        )
        save_file_url = await file_manager.save_file(
            file_path=file_path,
            file=upload_file,
        )
        return save_file_url

    @staticmethod
    async def download_message_file(
        download_data: DownloadMessageFileRequest,
        user: Users,
        session: AsyncSession,
    ) -> tuple[bytes, str, str]:
        """Скачивание файла сообщения (содержимое файла, content_type, имя_файла)"""
        # Проверка, что пользователь является участником чата
        await MessageService.check_user_is_member(
            user_id=user.id,
            chat_id=download_data.chat_id,
            chat_type=download_data.chat_type,
            session=session,
        )
        # Скачиваем файл
        file_manager = get_file_manager()
        file_path = Path(download_data.file_path)

        return await file_manager.download_file(file_path)

    @staticmethod
    async def delete_message_file(
        delete_data: DeleteMessageFileRequest,
        user: Users,
        session: AsyncSession,
    ) -> bool:
        """Удаление файла сообщения"""
        # Проверка, что пользователь является участником чата
        await MessageService.check_user_is_member(
            user_id=user.id,
            chat_id=delete_data.chat_id,
            chat_type=delete_data.chat_type,
            session=session,
        )
        # Удаляем файл
        file_manager = get_file_manager()
        file_path = Path(delete_data.file_path)
        return await file_manager.delete_file(file_path)
