__all__ = (
    "exception_handler",
    "BaseAppException",
    "InvalidTokenError",
    "TokenTypeMismatchError",
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "PhoneAlreadyExistsError",
    "UsernameAlreadyExistsError",
    "VerificationCodeExpiredError",
    "InvalidVerificationCodeError",
    "TooManyAttemptsError",
    "MemberAlreadyExistsError",
    "CreatorIsNotMemberError",
    "RecurringMembersError",
    "GroupNotFoundError",
    "UserIsNotGroupMemberError",
    "DialogAlreadyExistsError",
    "DialogWithOneUserError",
    "DialogNotFoundError",
    "UserIsNotDialogInterlocutorError",
    "NotCorrectMessageTypeForFileTypeError",
    "FilePathNotFoundError",
    "MissedDataForMessageTypeError",
    "MessageNotFoundError",
    "FutureTimestampMessageError",
    "StickerNotFoundError",
    "WebSocketMessageTypeNotFoundError",
)


from .handler import exception_handler
from .base import BaseAppException
from .errors.auth import InvalidTokenError, TokenTypeMismatchError
from .errors.users import (
    UserNotFoundError,
    UserAlreadyExistsError,
    PhoneAlreadyExistsError,
    UsernameAlreadyExistsError,
)
from .errors.verification import (
    VerificationCodeExpiredError,
    InvalidVerificationCodeError,
    TooManyAttemptsError,
)
from .errors.groups import (
    MemberAlreadyExistsError,
    CreatorIsNotMemberError,
    RecurringMembersError,
    GroupNotFoundError,
    UserIsNotGroupMemberError,
)
from .errors.dialogs import (
    DialogAlreadyExistsError,
    DialogWithOneUserError,
    DialogNotFoundError,
    UserIsNotDialogInterlocutorError,
)
from .errors.files import NotCorrectMessageTypeForFileTypeError, FilePathNotFoundError
from .errors.messages import (
    MissedDataForMessageTypeError,
    MessageNotFoundError,
    FutureTimestampMessageError,
)
from .errors.stickers import StickerNotFoundError
from .errors.websocket import WebSocketMessageTypeNotFoundError
