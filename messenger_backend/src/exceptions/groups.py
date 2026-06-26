from fastapi import status
from uuid import UUID

from .base import BaseAppException


class MemberAlreadyExistsError(BaseAppException):
    """ Участник уже есть в группе существует """
    def __init__(self, id: UUID):
        super().__init__(
            message=f"Участник с таким {id} уже есть в группе",
            status_code=status.HTTP_409_CONFLICT
        )


class RecurringMembers(BaseAppException):
    """ Повторение участников (при создании\обновлении) """
    def __init__(self):
        super().__init__(
            message=f"Участники не могут повторяться",
            status_code=status.HTTP_409_CONFLICT
        )


class CreatorIsNotMember(BaseAppException):
    """ Создатель группы не может быть просто участником (он админ)"""
    def __init__(self):
        super().__init__(
            message=f"Создатель группы не может указываться в качестве участника, т.к он по умолчанию является Админом",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )