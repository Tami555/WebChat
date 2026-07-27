from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile

from src.schemas import UploadMessageFileRequest, SaveMessageFileRequest
from src.models import Users
from src.utils.files import determining_file_type, get_file_manager
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
        real_file_type = determining_file_type(upload_file.content_type)
        if real_file_type != upload_data.file_type:
            raise NotCorrectMessageTypeForFileTypeError(
                upload_data.file_type, upload_file.content_type
            )

        # Сохраняем файл
        file_manager = get_file_manager()
        save_file_url = await file_manager.save_file(
            data=SaveMessageFileRequest(
                chat_id=upload_data.chat_id,
                file_type=upload_data.file_type,
                username=user.username,
            ),
            file=upload_file,
        )
        return save_file_url
