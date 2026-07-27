from fastapi import status

from ..base import BaseAppException


class VerificationCodeExpiredError(BaseAppException):
    """Действие кода истекло"""

    def __init__(self):
        super().__init__(
            message="Время действия кода верификации истекло",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidVerificationCodeError(BaseAppException):
    """Неверный код"""

    def __init__(self, attempts: int):
        super().__init__(
            message=f"Неверный код. { f"Осталось {attempts} попыток" if attempts else "Попыток больше нет"}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class TooManyAttemptsError(BaseAppException):
    """Слишком много попыток"""

    def __init__(self):
        super().__init__(
            message="Слишком много попыток", status_code=status.HTTP_400_BAD_REQUEST
        )
