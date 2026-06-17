from fastapi import status


class BaseAppException(Exception):
    """Базовое исключение приложения"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(message)