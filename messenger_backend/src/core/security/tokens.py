from .jwt import encode_jwt, decode_jwt
from src.core.config import get_settings
from src.schemas.enums import TokenType

settings = get_settings()


def create_jwt_token(
    type_token: TokenType,
    payload: dict,
    expire_minutes: int,
    secret_key: str = settings.auth.app_secret_key,
    algorithm: str = settings.auth.jwt_algorithm,
) -> bytes:
    """Генерация jwt токена по типу"""
    jwt_payload = {"type": type_token}
    jwt_payload.update(payload)

    token = encode_jwt(
        payload=jwt_payload,
        key=secret_key,
        algorithm=algorithm,
        expire_minutes=expire_minutes,
    )
    return token


def check_jwt_token_type(type_token: TokenType, token: bytes | str) -> dict | None:
    """Проверка типа jwt токена"""
    payload = decode_jwt(token)
    if payload["type"] != type_token:
        return None
    return payload
