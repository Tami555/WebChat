from datetime import datetime
from typing import Dict, Any, List


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

    @staticmethod
    def group_form_data(
        title: str = "Test Group",
        description: str | None = "Test group description",
        is_private: bool = False,
        members: list[str] | None = None,
    ) -> Dict[str, Any]:
        """Данные для группы в формате multipart/form-data"""
        return {
            "title": title,
            "description": description or "",
            "is_private": str(is_private).lower(),  # "true"/"false"
            "members": members or [],
        }

    @staticmethod
    def update_group_json(
        title: str | None = None,
        description: str | None = None,
        is_private: bool | None = None,
    ) -> Dict[str, Any]:
        """Данные для редактирования группы. Включает только переданные поля."""
        data = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if is_private is not None:
            data["is_private"] = is_private
        return data

    @staticmethod
    def add_members_json(members: List[str]) -> Dict[str, Any]:
        """JSON для добавления участников"""
        return {"members": members}

    @staticmethod
    def update_role_json(role: str) -> Dict[str, Any]:
        """JSON для изменения роли (role принимает 'admin' или 'member')"""
        return {"role": role}
