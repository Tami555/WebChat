from abc import abstractmethod, ABC
from uuid import uuid5, uuid4
from pathlib import Path
from fastapi import UploadFile
import aiofiles

from src.core.config import settings
from src.schemas import SaveMessageFileRequest


class FileManager(ABC):
    """Абстрактный менеджер для работы с файлами"""

    @staticmethod
    @abstractmethod
    async def save_file(
        data: SaveMessageFileRequest,
        file: UploadFile,
    ) -> str:
        raise NotImplementedError()


class LocalFileManager(FileManager):
    """Работа с файлами происходит на локальном диске"""

    @staticmethod
    async def save_file(
        data: SaveMessageFileRequest,
        file: UploadFile,
    ) -> str:
        USER_FILE_KEY = uuid5(uuid5(uuid4(), file.filename), data.username)
        BASE_PATH = Path(__file__).parent.parent.parent.parent
        FILES_PATH = BASE_PATH / "user_files" / "chats"
        USER_FILE_PATH = (
            FILES_PATH
            / str(data.chat_id)
            / data.file_type
            / f"{USER_FILE_KEY}_{file.filename}"
        )
        USER_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Сохраняем файл по 1 мб
        async with aiofiles.open(USER_FILE_PATH, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                await f.write(chunk)
        return str(USER_FILE_PATH)


class S3FileManager(FileManager):
    """Работа с файлами в S3 хранилище"""

    # TODO: Реальная загрузка через S3
    async def save_file(*args, **kwargs) -> str:
        return ""


def get_file_manager() -> type[FileManager]:
    """Фабрика для получения менеджера файлов"""
    if settings.app.environment == "production":
        return S3FileManager
    return LocalFileManager
