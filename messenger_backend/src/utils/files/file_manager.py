from abc import abstractmethod, ABC
from pathlib import Path
from fastapi import UploadFile
import aiofiles

from src.core.config import settings
from .file_helper import FilePathHelper


class FileManager(ABC):
    """Абстрактный менеджер для работы с файлами"""

    @staticmethod
    @abstractmethod
    async def save_file(
        file_path: Path,
        file: UploadFile,
    ) -> str:
        raise NotImplementedError()


class LocalFileManager(FileManager):
    """Работа с файлами происходит на локальном диске"""

    @staticmethod
    async def save_file(
        file_path: Path,
        file: UploadFile,
    ) -> str:

        save_file_path = FilePathHelper.get_local_base_media_dir() / file_path
        FilePathHelper.ensure_directory_exists(save_file_path)

        # Сохраняем файл по 1 мб
        async with aiofiles.open(save_file_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                await f.write(chunk)
        return str(save_file_path)


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
