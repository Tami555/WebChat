from src.core.config import settings
from src.core.security.tokens import create_jwt_token
from src.schemas.enums import TokenType


class TokenFactory:
    """Фабрика для создания токенов в тестах"""

    @staticmethod
    def create_access_token(
        username: str,
        expired: bool = False,
    ) -> bytes:
        """Создает access токен"""
        return create_jwt_token(
            type_token=TokenType.ACCESS_TOKEN,
            payload={"sub": username},
            expire_minutes=0 if expired else settings.auth.expire_access_token_minutes,
        )

    @staticmethod
    def create_refresh_token(
        username: str,
        expired: bool = False,
    ) -> bytes:
        """Создает refresh токен"""
        return create_jwt_token(
            type_token=TokenType.REFRESH_TOKEN,
            payload={"sub": username},
            expire_minutes=0 if expired else settings.auth.expire_refresh_token_minutes,
        )

    @staticmethod
    def create_expired_access_token(username: str) -> bytes:
        """Создает просроченный access токен"""
        return TokenFactory.create_access_token(username, expired=True)

    @staticmethod
    def create_expired_refresh_token(username: str) -> bytes:
        """Создает просроченный refresh токен"""
        return TokenFactory.create_refresh_token(username, expired=True)
