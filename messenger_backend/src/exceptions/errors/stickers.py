from fastapi import status

from ..base import BaseAppException


class StickerNotFoundError(BaseAppException):
    """ Стикер не найден """
    def __init__(self):
        super().__init__(
            message="Стикер не найден",
            status_code=status.HTTP_404_NOT_FOUND
        )