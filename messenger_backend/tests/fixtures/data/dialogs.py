from datetime import datetime
from typing import Dict, Any, Optional


class DialogDataFactory:
    """Фабрика данных для диалогов"""

    @staticmethod
    def dialog_data() -> Dict[str, Any]:
        """Данные для диалога"""
        return {
            "created_at": datetime.now(),
        }

    @staticmethod
    def create_dialog_custom(**kwargs) -> Dict[str, Any]:
        """Создание кастомного диалога"""
        defaults = DialogDataFactory.dialog_data()
        defaults.update(kwargs)
        return defaults

    @staticmethod
    def message_data(
        content: str = "Test message content",
        type: str = "TEXT",
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
    def message_status_data(
        is_read: bool = False,
        read_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Данные для статуса сообщения"""
        return {
            "is_read": is_read,
            "read_at": read_at if is_read else None,
        }

    @staticmethod
    def create_message_custom(**kwargs) -> Dict[str, Any]:
        """Создание кастомного сообщения"""
        defaults = ChatDataFactory.message_data()
        defaults.update(kwargs)
        return defaults
