from fastapi import status

from ..base import BaseAppException


class NotCorrectMessageTypeForFileTypeError(BaseAppException):
    """Тип сообщения не соответствует переданному типу файла"""

    def __init__(self, message_type: str, file_type: str):
        super().__init__(
            message=f"Для типа сообщения {message_type}, не подходит тип файла {file_type}",
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        )


class FilePathNotFoundError(BaseAppException):
    """Файл не найден"""

    def __init__(self):
        super().__init__(
            message="Файл не найден",
            status_code=status.HTTP_404_NOT_FOUND,
        )
