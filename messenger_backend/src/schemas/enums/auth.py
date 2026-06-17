from enum import StrEnum as PyEnum


class TokenType(PyEnum):
    ACCESS_TOKEN = "access"
    REFRESH_TOKEN = "refresh"