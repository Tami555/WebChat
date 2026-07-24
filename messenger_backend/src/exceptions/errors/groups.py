from fastapi import status
from uuid import UUID

from ..base import BaseAppException


class MemberAlreadyExistsError(BaseAppException):
    """ Участник уже есть в группе """
    def __init__(self, user_id: UUID):
        super().__init__(
            message=f"Участник с таким {user_id} уже есть в группе",
            status_code=status.HTTP_409_CONFLICT
        )


class RecurringMembersError(BaseAppException):
    """ Повторение участников (при создании/обновлении) """
    def __init__(self):
        super().__init__(
            message=f"Участники не могут повторяться",
            status_code=status.HTTP_409_CONFLICT
        )


class CreatorIsNotMemberError(BaseAppException):
    """ Создатель группы не может быть просто участником (он админ)"""
    def __init__(self):
        super().__init__(
            message=f"Создатель группы не может указываться в качестве участника, т.к он по умолчанию является Админом",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )


class GroupNotFoundError(BaseAppException):
    """ Группа не найдена """
    def __init__(self):
        super().__init__(
            message="Группа не найдена",
            status_code=status.HTTP_404_NOT_FOUND
        )


class UserIsNotGroupMemberError(BaseAppException):
    """ Пользователь не является участником группы """
    def __init__(self):
        super().__init__(
            message="Вы не являетесь участником группы",
            status_code=status.HTTP_403_FORBIDDEN
        )
