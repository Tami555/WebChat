from fastapi import status

from ..base import BaseAppException


class InvalidTokenError(BaseAppException):
    """ Невалидный токен """
    def __init__(self):
        super().__init__(
            message="Невалидный токен",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class TokenTypeMismatchError(BaseAppException):
    """ Неверный тип токена """
    def __init__(self, expected: str):
        super().__init__(
            message=f"Неверный тип токена. Ожидался: {expected}",
            status_code=status.HTTP_401_UNAUTHORIZED
        )