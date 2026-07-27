from enum import StrEnum as PyEnum


class ChatType(PyEnum):
    """Типы чатов"""

    DIALOGS = "dialog"  # чат-диалог
    GROUP = "group"  # группа
