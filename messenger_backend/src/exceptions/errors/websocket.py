from fastapi import status

from ..base import BaseAppException


class WebSocketMessageTypeNotFoundError(BaseAppException):
    """Тип сообщения WebSocket не был найден"""

    def __init__(self):
        super().__init__(
            message="Тип WebSocket-сообщения не был найден",
            status_code=status.HTTP_404_NOT_FOUND,
        )
