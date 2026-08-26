from datetime import datetime
from typing import Dict, Any

from src.schemas.enums import MessageType


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
