from datetime import datetime
from uuid import UUID
from typing import Dict, Any


class DialogDataFactory:
    """Фабрика данных для диалогов"""

    @staticmethod
    def dialog_data() -> Dict[str, Any]:
        """Данные для диалога"""
        return {
            "created_at": datetime.now(),
        }

    @staticmethod
    def create_dialog(interlocutor_id: UUID) -> Dict[str, Any]:
        """Создание диалога"""
        return {"interlocutor": str(interlocutor_id)}
