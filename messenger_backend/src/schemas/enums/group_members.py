from enum import StrEnum as PyEnum


class GroupMemberRole(PyEnum):
    """ Типы ролей в группе """
    ADMIN = 'admin'  # Админ
    MEMBER = 'member'  # Участник
