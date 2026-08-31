from fastapi import status

from ..base import BaseAppException


class MissedDataForMessageTypeError(BaseAppException):
    """Сообщение определенного типа не содержит необходимые атрибуты данных"""

    def __init__(self, message_type: str, data: tuple):
        super().__init__(
            message=f"Для типа сообщения {message_type}, необходимо указать данные {",".join(data)}",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        )


class MessageNotFoundError(BaseAppException):
    """Сообщение не найдено"""

    def __init__(self):
        super().__init__(
            message="Сообщение не найдено", status_code=status.HTTP_404_NOT_FOUND
        )


class FutureTimestampMessageError(BaseAppException):
    """Дата сообщения в будущем"""

    def __init__(self):
        super().__init__(
            message="Дата сообщения не может быть в будущем",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
