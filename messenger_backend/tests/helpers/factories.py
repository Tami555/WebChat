from uuid import UUID
from pathlib import Path

from src.core.config import settings
from src.core.security.tokens import create_jwt_token
from src.schemas.enums import TokenType


class TokenFactory:
    """Фабрика для создания токенов в тестах"""

    @staticmethod
    def create_access_token(
        username: str,
        expired: bool = False,
    ) -> bytes:
        """Создает access токен"""
        return create_jwt_token(
            type_token=TokenType.ACCESS_TOKEN,
            payload={"sub": username},
            expire_minutes=0 if expired else settings.auth.expire_access_token_minutes,
        )

    @staticmethod
    def create_refresh_token(
        username: str,
        expired: bool = False,
    ) -> bytes:
        """Создает refresh токен"""
        return create_jwt_token(
            type_token=TokenType.REFRESH_TOKEN,
            payload={"sub": username},
            expire_minutes=0 if expired else settings.auth.expire_refresh_token_minutes,
        )

    @staticmethod
    def create_expired_access_token(username: str) -> bytes:
        """Создает просроченный access токен"""
        return TokenFactory.create_access_token(username, expired=True)

    @staticmethod
    def create_expired_refresh_token(username: str) -> bytes:
        """Создает просроченный refresh токен"""
        return TokenFactory.create_refresh_token(username, expired=True)


class FileFactory:
    """Фабрика для работы с файлами в тестах"""

    @staticmethod
    def get_file_content_type(file_path: Path) -> str:
        """Определяет content-type по расширению файла"""
        suffix = file_path.suffix.lower()
        content_types = {
            ".txt": "text/plain",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".mp4": "video/mp4",
        }
        return content_types.get(suffix, "application/octet-stream")

    @staticmethod
    def cleanup_test_messages_files(chat_id: UUID):
        """Удаляет тестовые файлы после тестов"""
        import shutil
        from pathlib import Path

        BASE_PATH = Path(__file__).parent.parent.parent / "test_media"
        FILES_PATH = BASE_PATH / "user_files" / "chats" / str(chat_id)

        if FILES_PATH.exists():
            shutil.rmtree(FILES_PATH)
