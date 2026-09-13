from abc import abstractmethod, ABC
from pathlib import Path
from fastapi import UploadFile
import aiofiles

from src.core.config import get_settings
from src.exceptions import FilePathNotFoundError
from .file_helper import FilePathHelper, get_content_type_by_extension


class FileManager(ABC):
    """Абстрактный менеджер для работы с файлами"""

    @staticmethod
    @abstractmethod
    async def save_file(
        file_path: Path,
        file: UploadFile,
    ) -> str:
        """Сохраняет файл"""
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    async def download_file(file_path: Path) -> tuple[bytes, str, str]:
        """Скачивает файл"""
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    async def delete_file(
        file_path: Path,
    ) -> bool:
        """Удаляет файл"""
        raise NotImplementedError()


class LocalFileManager(FileManager):
    """Работа с файлами происходит на локальном диске"""

    @staticmethod
    async def save_file(
        file_path: Path,
        file: UploadFile,
    ) -> str:
        """Сохранение файла на локальный диск"""
        save_file_path = FilePathHelper.get_local_base_media_dir() / file_path
        FilePathHelper.ensure_directory_exists(save_file_path)

        # Сохраняем файл по 1 мб
        async with aiofiles.open(save_file_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                await f.write(chunk)
        return str(file_path)

    @staticmethod
    async def download_file(file_path: Path) -> tuple[bytes, str, str]:
        """Скачивание файла с локального диска"""
        full_path = FilePathHelper.get_local_base_media_dir() / file_path
        if not full_path.exists():
            raise FilePathNotFoundError()

        filename = FilePathHelper.extract_filename_from_message_file_path(full_path)
        content_type = get_content_type_by_extension(full_path.suffix)

        # читаем файл
        async with aiofiles.open(full_path, "rb") as f:
            content = await f.read()

        return content, content_type, filename

    @staticmethod
    async def delete_file(file_path: Path) -> bool:
        """Удаляет файл с локального диска"""
        full_path = FilePathHelper.get_local_base_media_dir() / file_path

        if not full_path.exists():
            return False

        # удаляем файл
        full_path.unlink()
        return True


class S3FileManager(FileManager):
    """Работа с файлами в S3 хранилище"""

    # TODO: Реальная работа через S3
    @staticmethod
    async def save_file(*args, **kwargs) -> str:
        """Сохраняет файл в S3"""
        pass

    @staticmethod
    async def download_file(file_path: Path) -> tuple[bytes, str, str]:
        """Скачивает файл из S3"""
        pass

    @staticmethod
    async def delete_file(file_path: Path) -> bool:
        """Удаляет файл из S3"""
        pass


def get_file_manager() -> type[FileManager]:
    """Фабрика для получения менеджера файлов"""
    settings = get_settings()
    if settings.app.environment == "production":
        return S3FileManager
    return LocalFileManager
