from datetime import datetime
from typing import Dict, Any, Optional

from src.schemas.enums import MessageType, ChatType


class MessagesDataFactory:
    """Фабрика данных для сообщений"""

    @staticmethod
    def message_data(
        content: str = "Test message content",
        type: str = MessageType.TEXT,
    ) -> Dict[str, Any]:
        """Данные для сообщения"""
        return {
            "type": type,
            "content": content,
            "created_at": datetime.now(),
            "is_deleted": False,
            "is_edited": False,
        }

    @staticmethod
    def create_message_data(
        chat_type: ChatType,
        content: Optional[str] = "Test message content",
        message_type: str = MessageType.TEXT,
        **kwargs
    ) -> Dict[str, Any]:
        """Данные для создания сообщения (по умолчанию сообщение типа TEXT)"""
        data = {
            "chat_type": chat_type,
            "message_type": message_type,
            "content": content,
            "created_at": datetime.now().isoformat(),
        }
        data.update(kwargs)
        return data

    @staticmethod
    def message_status_data(is_read: bool = False) -> Dict[str, Any]:
        """Данные для статуса сообщения"""
        return {
            "is_read": is_read,
            "read_at": datetime.now() if is_read else None,
        }

    @staticmethod
    def create_message_custom(**kwargs) -> Dict[str, Any]:
        """Создание кастомного сообщения"""
        defaults = MessagesDataFactory.message_data()
        defaults.update(kwargs)
        return defaults
