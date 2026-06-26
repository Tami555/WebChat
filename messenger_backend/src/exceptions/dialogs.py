from fastapi import status

from .base import BaseAppException


class DialogAlreadyExistsError(BaseAppException):
    """ Диалог уже существует """
    def __init__(self):
        super().__init__(
            message=f"Диалог с таким пользователем уже существует",
            status_code=status.HTTP_409_CONFLICT
        )


class DialogWithOneUserError(BaseAppException):
    """ Диалог с одним пользователем """
    def __init__(self):
        super().__init__(
            message=f"Диалог с одним пользователем не может существовать",
            status_code=status.HTTP_400_BAD_REQUEST
        )