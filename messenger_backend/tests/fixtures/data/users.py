from datetime import datetime
from typing import Dict, Any


class UserDataFactory:
    """Фабрика данных пользователей"""

    @staticmethod
    def user_1() -> Dict[str, Any]:
        return {
            "username": "tami",
            "phone": "tel:+7-917-123-45-67",
            "code": "234567",
            "last_seen": datetime.now(),
        }

    @staticmethod
    def user_2() -> Dict[str, Any]:
        return {
            "username": "tobbi",
            "phone": "tel:+7-919-987-65-43",
            "code": "876543",
            "last_seen": datetime.now(),
        }

    @staticmethod
    def user_3() -> Dict[str, Any]:
        return {
            "username": "anna",
            "phone": "tel:+7-917-254-19-12",
            "code": "541912",
            "last_seen": datetime.now(),
        }

    @staticmethod
    def create_user_custom(**kwargs) -> Dict[str, Any]:
        """Создание кастомного пользователя"""
        defaults = {
            "username": "custom_user",
            "phone": "tel:+7-999-000-00-00",
            "code": "000000",
            "last_seen": datetime.now(),
        }
        defaults.update(kwargs)
        return defaults
