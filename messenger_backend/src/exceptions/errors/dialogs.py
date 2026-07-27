from fastapi import status

from ..base import BaseAppException


class DialogAlreadyExistsError(BaseAppException):
    """Диалог уже существует"""

    def __init__(self):
        super().__init__(
            message=f"Диалог с таким пользователем уже существует",
            status_code=status.HTTP_409_CONFLICT,
        )


class DialogWithOneUserError(BaseAppException):
    """Диалог с одним пользователем"""

    def __init__(self):
        super().__init__(
            message=f"Диалог с одним пользователем не может существовать",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class DialogNotFoundError(BaseAppException):
    """Диалог не найден"""

    def __init__(self):
        super().__init__(
            message="Диалог не найден", status_code=status.HTTP_404_NOT_FOUND
        )


class UserIsNotDialogInterlocutorError(BaseAppException):
    """Пользователь не является участником диалога"""

    def __init__(self):
        super().__init__(
            message="Вы не являетесь участником данного диалога",
            status_code=status.HTTP_403_FORBIDDEN,
        )
