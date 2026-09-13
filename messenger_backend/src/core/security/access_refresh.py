from src.models import Users
from src.core.config import get_settings
from src.schemas import AccessTokenContent, RefreshTokenContent
from src.schemas.enums import TokenType
from .tokens import create_jwt_token, check_jwt_token_type

settings = get_settings()


# Генерация токенов
def create_access_token(user: Users):
    """Генерация access токена"""
    payload = AccessTokenContent.from_user(user)
    return create_jwt_token(
        type_token=TokenType.ACCESS_TOKEN,
        payload=payload,
        expire_minutes=settings.auth.expire_access_token_minutes,
    )


def create_refresh_token(user: Users):
    """Генерация refresh токена"""
    payload = RefreshTokenContent.from_user(user)
    return create_jwt_token(
        type_token=TokenType.REFRESH_TOKEN,
        payload=payload,
        expire_minutes=settings.auth.expire_refresh_token_minutes,
    )


# Проверки токенов на тип
def check_access_token(token: bytes | str):
    """Проверка, что токен типа access"""
    return check_jwt_token_type(TokenType.ACCESS_TOKEN, token)


def check_refresh_token(token: bytes | str):
    """Проверка, что токен типа refresh"""
    return check_jwt_token_type(TokenType.REFRESH_TOKEN, token)
