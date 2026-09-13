from pathlib import Path
from uuid import uuid5, uuid4, UUID

from src.core.config import get_settings
from src.schemas.enums import MessageType, ChatType


class FilePathHelper:
    """Помощник для генерации путей файлов"""

    @staticmethod
    def generate_message_file_path(
        chat_id: UUID,
        file_type: MessageType,
        filename: str,
        username: str,
    ) -> Path:
        """
        Генерирует путь для файла сообщения пользователя
        Структура: user_files/chats/{chat_id}/{file_type}/{uuid}_{filename}
        """
        file_key = uuid5(uuid5(uuid4(), filename), username)
        file_path = (
            Path("user_files")
            / "chats"
            / str(chat_id)
            / str(file_type)
            / f"{file_key}_{filename}"
        )
        return file_path

    @staticmethod
    def extract_filename_from_message_file_path(file_path: Path) -> str:
        """Извлекает имя файла из полного пути файла сообщения"""
        filename = Path(file_path).name
        artifacts = str(filename).split("_")
        return "".join(artifacts[1:])

    @staticmethod
    def generate_sticker_file_path(
        sticker_id: UUID,
        pack_id: UUID,
        filename: str,
    ) -> Path:
        """
        Генерирует путь для файла стикера
        Структура: stickers/{pack_id}/{sticker_id}_{filename}
        """
        file_path = Path("stickers") / str(pack_id) / f"{sticker_id}_{filename}"
        return file_path

    @staticmethod
    def generate_avatar_file_path(user_id: UUID, filename: str) -> Path:
        """
        Генерирует путь для аватарки пользователя
        Структура: avatars/{user_id}_{filename}
        """
        file_path = Path("avatars") / f"{user_id}_{filename}"
        return file_path

    @staticmethod
    def generate_chat_avatar_file_path(
        chat_id: UUID,
        chat_type: ChatType,
        filename: str,
    ) -> Path:
        """
        Генерирует путь для аватарки чата
        Структура: chat_avatars/{chat_type}/{chat_id}_{filename}
        """
        file_path = Path("chat_avatars") / f"{str(chat_type)}" / f"{chat_id}_{filename}"
        return file_path

    @staticmethod
    def ensure_directory_exists(file_path: Path) -> None:
        """Создает директорию для файла, если её нет"""
        file_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_local_base_media_dir() -> Path:
        """Определяет директорию работы с файлами на локалке, исходе из окружения"""
        settings = get_settings()

        base_path = Path(__file__).parent.parent.parent.parent
        return base_path / (
            "test_media" if settings.app.environment == "testing" else "media"
        )


def get_file_type_for_message(file_content_type: str) -> MessageType | None:
    """Определяет тип файла для сообщения"""
    content_type = file_content_type.strip().split("/")[0]
    match content_type:
        case "audio":
            return MessageType.VOICE

        case file_type if file_type in ["image", "video"]:
            return MessageType.IMAGE

        case file_type if file_type in ["text", "application", "font"]:
            return MessageType.FILE

        case _:
            return None


def get_content_type_by_extension(extension: str) -> str:
    """Возвращает MIME-тип по расширению файла"""
    content_types = {
        ".txt": "text/plain",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".mp4": "video/mp4",
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".xls": "application/vnd.ms-excel",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".zip": "application/zip",
        ".rar": "application/x-rar-compressed",
    }
    return content_types.get(extension.lower(), "application/octet-stream")
