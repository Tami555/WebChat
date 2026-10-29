from uuid import UUID
from fastapi import UploadFile
from pathlib import Path

from src.core.config import get_settings
from src.schemas import (
    UploadMessageFileRequest,
    DownloadMessageFileRequest,
    DeleteMessageFileRequest,
)
from src.utils.files import (
    get_file_type_for_message,
    get_file_manager,
    is_image_file,
    FilePathHelper,
)
from src.exceptions import (
    NotCorrectMessageTypeForFileTypeError,
    InvalidAvatarFileError,
    FileSizeTooLargeError,
)


class FileService:
    """Сервис для работы с файлами"""

    settings = get_settings()

    @staticmethod
    async def check_avatar_size(avatar: UploadFile):
        max_size = FileService.settings.files.avatar_max_size_mb
        content = await avatar.read()
        if len(content) > max_size * 1024 * 1024:
            raise FileSizeTooLargeError(max_size_mb=max_size)
        # Возвращаем курсор файла в начало
        await avatar.seek(0)
        return True

    @staticmethod
    async def upload_message_file(
        upload_data: UploadMessageFileRequest, upload_file: UploadFile, username: str
    ):
        """Проверка корректности и загрузка файла сообщения"""
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
            username=username,
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
    ) -> tuple[bytes, str, str]:
        """Скачивание файла сообщения (содержимое файла, content_type, имя_файла)"""
        # Скачиваем файл
        file_manager = get_file_manager()
        file_path = Path(download_data.file_path)

        return await file_manager.download_file(file_path)

    @staticmethod
    async def delete_message_file(delete_data: DeleteMessageFileRequest) -> bool:
        """Удаление файла сообщения"""
        # Удаляем файл
        file_manager = get_file_manager()
        file_path = Path(delete_data.file_path)
        return await file_manager.delete_file(file_path)

    @staticmethod
    async def upload_group_avatar(
        group_id: UUID,
        avatar: UploadFile,
    ) -> str:
        """Загрузка аватарки группы"""
        if not is_image_file(avatar.content_type):
            raise InvalidAvatarFileError(avatar.content_type)

        await FileService.check_avatar_size(avatar)

        file_manager = get_file_manager()
        file_path = FilePathHelper.generate_group_avatar_path(
            group_id=group_id,
            filename=avatar.filename,
        )
        return await file_manager.save_file(file_path=file_path, file=avatar)

    @staticmethod
    async def upload_user_avatar(
        user_id: UUID,
        avatar: UploadFile,
    ) -> str:
        """Загрузка аватарки пользователя"""
        if not is_image_file(avatar.content_type):
            raise InvalidAvatarFileError(avatar.content_type)

        await FileService.check_avatar_size(avatar)

        file_manager = get_file_manager()
        file_path = FilePathHelper.generate_user_avatar_path(
            user_id=user_id,
            filename=avatar.filename,
        )
        return await file_manager.save_file(file_path=file_path, file=avatar)

    @staticmethod
    async def delete_group_avatar(avatar_url: str | None) -> bool:
        """Удаление аватарки группы"""
        if not avatar_url:
            return False
        file_manager = get_file_manager()
        return await file_manager.delete_file(Path(avatar_url))

    @staticmethod
    async def delete_user_avatar(avatar_url: str | None) -> bool:
        """Удаление аватарки пользователя"""
        if not avatar_url:
            return False
        file_manager = get_file_manager()
        return await file_manager.delete_file(Path(avatar_url))

    @staticmethod
    async def delete_all_chat_files(chat_id: UUID) -> bool:
        """Удаляет директорию со всеми файлами чата"""
        file_manager = get_file_manager()
        dir_path = Path("user_files") / "chats" / str(chat_id)
        return await file_manager.delete_directory(dir_path)
