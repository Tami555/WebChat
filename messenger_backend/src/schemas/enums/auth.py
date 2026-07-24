from enum import StrEnum as PyEnum


class TokenType(PyEnum):
    """ Типы токенов """
    ACCESS_TOKEN = "access"
    REFRESH_TOKEN = "refresh"
