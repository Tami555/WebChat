from uuid import UUID
from fastapi import status

from ..base import BaseAppException


class UserAlreadyExistsError(BaseAppException):
    """Пользователь уже существует"""

    def __init__(self, field: str):
        super().__init__(
            message=f"Пользователь с таким {field} уже существует",
            status_code=status.HTTP_409_CONFLICT,
        )


class PhoneAlreadyExistsError(UserAlreadyExistsError):
    """Пользователь с таким телефоном уже существует"""

    def __init__(self):
        super().__init__("телефоном")


class UsernameAlreadyExistsError(UserAlreadyExistsError):
    """Пользователь с таким username уже существует"""

    def __init__(self):
        super().__init__("username")


class UserNotFoundError(BaseAppException):
    """Пользователь не найден"""

    def __init__(self, user_id: UUID | None = None):
        msg = (
            "Пользователь не найден"
            if user_id is None
            else f"Пользователь c {user_id} не найден"
        )
        super().__init__(message=msg, status_code=status.HTTP_404_NOT_FOUND)
