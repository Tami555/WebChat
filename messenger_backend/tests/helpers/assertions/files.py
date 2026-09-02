from pathlib import Path
from uuid import UUID

from tests.helpers.factories import FileFactory


class FilesAssertions:
    """Проверки Файлов"""

    @staticmethod
    def assert_file_exists(file_path: str):
        """Проверка, что файл существует"""
        base_path = Path(__file__).parent.parent.parent.parent / "test_media"
        assert (base_path / file_path).exists()

    @staticmethod
    def assert_file_not_exists(file_path: str):
        """Проверка, что файла не существует"""
        base_path = Path(__file__).parent.parent.parent.parent / "test_media"
        assert (base_path / file_path).exists() is False

    @staticmethod
    def assert_file_exists_and_delete(file_path: str, chat_id: UUID):
        """Проверка, что файл существует и последующее его удаление"""
        FilesAssertions.assert_file_exists(file_path)
        FileFactory.cleanup_test_messages_files(chat_id)
