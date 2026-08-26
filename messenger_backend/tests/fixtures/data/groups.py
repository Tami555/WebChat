from datetime import datetime
from typing import Dict, Any


class GroupsDataFactory:
    """Фабрика данных для групп"""

    @staticmethod
    def group_data(
        title: str = "Test Group",
        description: str = "Test group description",
        is_private: bool = False,
    ) -> Dict[str, Any]:
        """Данные для группы"""
        return {
            "title": title,
            "description": description,
            "is_private": is_private,
            "created_at": datetime.now(),
        }

    @staticmethod
    def create_group_custom(**kwargs) -> Dict[str, Any]:
        """Создание кастомной группы"""
        defaults = GroupsDataFactory.group_data()
        defaults.update(kwargs)
        return defaults
